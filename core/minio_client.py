import hashlib
import hmac
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse


def _sign(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _get_signature_key(key: str, date_stamp: str, region: str, service: str) -> bytes:
    k_date = _sign(("AWS4" + key).encode("utf-8"), date_stamp)
    k_region = _sign(k_date, region)
    k_service = _sign(k_region, service)
    return _sign(k_service, "aws4_request")


def _s3_request(
    method: str,
    canonical_uri: str,
    data: bytes = b"",
    content_type: str = "",
    query: str = "",
) -> int:
    endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000").rstrip("/")
    access_key = os.getenv("MINIO_ROOT_USER", "minioadmin")
    secret_key = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
    region = "us-east-1"
    service = "s3"

    parsed = urlparse(endpoint)
    host = parsed.netloc
    url = f"{endpoint}{canonical_uri}" + (f"?{query}" if query else "")

    now = datetime.now(timezone.utc)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")
    payload_hash = hashlib.sha256(data).hexdigest()

    header_map: Dict[str, str] = {
        "host": host,
        "x-amz-content-sha256": payload_hash,
        "x-amz-date": amz_date,
    }
    if content_type:
        header_map["content-type"] = content_type

    sorted_keys = sorted(header_map.keys())
    canonical_headers = "".join(f"{k}:{header_map[k]}\n" for k in sorted_keys)
    signed_headers = ";".join(sorted_keys)
    canonical_request = (
        f"{method}\n{canonical_uri}\n{query}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
    )

    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    string_to_sign = (
        f"AWS4-HMAC-SHA256\n{amz_date}\n{credential_scope}\n"
        f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    )

    signing_key = _get_signature_key(secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    auth_header = (
        f"AWS4-HMAC-SHA256 Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    req_headers = {
        "x-amz-date": amz_date,
        "x-amz-content-sha256": payload_hash,
        "Authorization": auth_header,
    }
    if content_type:
        req_headers["Content-Type"] = content_type

    req = urllib.request.Request(url, data=data if data or method == "PUT" else None, method=method, headers=req_headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status


def ensure_public_bucket(bucket: str = "media") -> None:
    try:
        _s3_request("PUT", f"/{bucket}")
    except urllib.error.HTTPError as exc:
        if exc.code not in (409, 200):
            raise

    policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket}/*"],
            }
        ],
    }).encode("utf-8")
    _s3_request("PUT", f"/{bucket}", data=policy, content_type="application/json", query="policy=")


def upload_bytes_to_minio(
    object_name: str,
    data: bytes,
    content_type: str = "application/octet-stream",
    bucket: str = "media",
) -> str:
    """Upload bytes to MinIO S3 using AWS SigV4 (stdlib-only) and return proxied /media/<object_name> path."""
    ensure_public_bucket(bucket)
    status = _s3_request("PUT", f"/{bucket}/{object_name}", data=data, content_type=content_type)
    if status not in (200, 201, 204):
        raise RuntimeError(f"MinIO upload failed with status {status}")
    return f"/{bucket}/{object_name}"


def ensure_minio_media_seeded(bucket: str = "media") -> None:
    """Ensure MinIO public bucket and seed camera_*.jpg / video_*.mp4 exist."""
    static_media = Path(__file__).resolve().parent.parent / "static" / "media"
    if not static_media.exists():
        return
    try:
        ensure_public_bucket(bucket)
        for file_path in sorted(static_media.iterdir()):
            if not file_path.is_file():
                continue
            ext = file_path.suffix.lower()
            ctype = "image/jpeg" if ext in (".jpg", ".jpeg") else "video/mp4" if ext == ".mp4" else "application/octet-stream"
            _s3_request("PUT", f"/{bucket}/{file_path.name}", data=file_path.read_bytes(), content_type=ctype)
    except Exception:
        # MinIO может быть не запущен в автономных юнит-тестах
        pass
