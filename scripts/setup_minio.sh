#!/usr/bin/env bash
set -e

echo "=== Инициализация MinIO хранилища ==="
docker compose up -d

echo "Ожидание готовности MinIO..."
sleep 3

docker exec minio_storage mc alias set myminio http://localhost:9000 minioadmin minioadmin
docker exec minio_storage mc mb --ignore-existing myminio/media
docker exec minio_storage mc anonymous set public myminio/media
docker exec minio_storage mc mb --ignore-existing myminio/cctv-media
docker exec minio_storage mc anonymous set public myminio/cctv-media

for file in _references/camera_*.jpg _references/video_*.mp4; do
    filename=$(basename "$file")
    docker cp "$file" "minio_storage:/tmp/$filename"
    docker exec minio_storage mc cp "/tmp/$filename" "myminio/media/$filename"
    docker exec minio_storage mc cp "/tmp/$filename" "myminio/cctv-media/$filename"
done

echo "=== Медиафайлы успешно загружены в MinIO ==="
docker exec minio_storage mc ls myminio/media/
docker exec minio_storage mc ls myminio/cctv-media/
