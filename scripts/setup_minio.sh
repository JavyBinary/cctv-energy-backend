#!/usr/bin/env bash
set -e

echo "=== Инициализация MinIO хранилища ==="
docker compose up -d 2>/dev/null || true

echo "Ожидание готовности MinIO..."
sleep 3

# Определение идентификатора или имени работающего контейнера MinIO
MINIO_CONTAINER=$(docker ps --filter "ancestor=minio/minio" --filter "status=running" --format "{{.ID}}" | head -n 1)
if [ -z "$MINIO_CONTAINER" ]; then
    MINIO_CONTAINER=$(docker compose ps -q minio 2>/dev/null || true)
fi
if [ -z "$MINIO_CONTAINER" ]; then
    MINIO_CONTAINER="minio_storage"
fi

echo "Используется контейнер MinIO: $MINIO_CONTAINER"

docker exec "$MINIO_CONTAINER" mc alias set myminio http://localhost:9000 minioadmin minioadmin
docker exec "$MINIO_CONTAINER" mc mb --ignore-existing myminio/media
docker exec "$MINIO_CONTAINER" mc anonymous set public myminio/media
docker exec "$MINIO_CONTAINER" mc mb --ignore-existing myminio/cctv-media
docker exec "$MINIO_CONTAINER" mc anonymous set public myminio/cctv-media

# Поиск директории с медиафайлами
if [ -d "static/media" ]; then
    REF_DIR="static/media"
elif [ -d "_references" ]; then
    REF_DIR="_references"
elif [ -d "../_references" ]; then
    REF_DIR="../_references"
elif [ -d "../../_references" ]; then
    REF_DIR="../../_references"
else
    echo "Ошибка: директория с медиафайлами не найдена!"
    exit 1
fi

echo "Копирование медиафайлов из $REF_DIR..."
for file in "$REF_DIR"/camera_*.jpg "$REF_DIR"/video_*.mp4; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        docker cp "$file" "$MINIO_CONTAINER:/tmp/$filename"
        docker exec "$MINIO_CONTAINER" mc cp "/tmp/$filename" "myminio/media/$filename"
        docker exec "$MINIO_CONTAINER" mc cp "/tmp/$filename" "myminio/cctv-media/$filename"
    fi
done

echo "=== Медиафайлы успешно загружены в MinIO ==="
docker exec "$MINIO_CONTAINER" mc ls myminio/media/
docker exec "$MINIO_CONTAINER" mc ls myminio/cctv-media/
