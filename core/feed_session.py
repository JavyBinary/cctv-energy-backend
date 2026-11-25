import json
import uuid
from typing import Any, Dict, List, Optional

from core.session import get_redis_client

FEED_PREFIX = "cameras:feed:"
FEED_BATCH_SIZE = 100
FEED_SESSION_TTL = 1800  # 30 минут


def validate_or_create_session_id(session_id: Optional[str]) -> str:
    if not session_id:
        return uuid.uuid4().hex
    cleaned = session_id.strip()
    try:
        parsed = uuid.UUID(cleaned)
    except ValueError as exc:
        raise ValueError("Invalid feed session_id") from exc
    return parsed.hex


def build_feed_storage_key(session_id: str, user_id: Optional[int] = None) -> str:
    if user_id is not None:
        return f"user:{user_id}"
    return f"guest:{session_id}"


async def load_feed_batch(storage_key: str) -> Optional[Dict[str, Any]]:
    client = get_redis_client()
    if client is None:
        raise RuntimeError("Redis client is not initialized")
    raw = await client.get(f"{FEED_PREFIX}{storage_key}")
    if raw is None:
        return None
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get("ids"), list):
        return None
    return data


async def save_feed_batch(
    storage_key: str,
    session_id: str,
    batch_number: int,
    first_position: int,
    ids: List[int],
    ttl: int = FEED_SESSION_TTL,
) -> Dict[str, Any]:
    client = get_redis_client()
    if client is None:
        raise RuntimeError("Redis client is not initialized")
    payload: Dict[str, Any] = {
        "session_id": session_id,
        "batch_number": batch_number,
        "first_position": first_position,
        "ids": ids,
    }
    await client.set(
        f"{FEED_PREFIX}{storage_key}",
        json.dumps(payload),
        ex=ttl,
    )
    return payload
