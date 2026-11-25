# CCTV Energy Backend — Доп 2 (Tauri + CLIP)

Автономная папка бэкенда для ветки **`tauri`** в репозитории `cctv-energy-backend`.

## Изменения для нативного приложения Tauri + ИИ-поиска (CLIP / SigLIP)
- Добавлена миграция Alembic `b2d9e41c7a10_add_description_en_to_cameras.py` (колонка `description_en VARCHAR(100)`).
- В `CameraResponse` (`GET /api/cameras`, `GET /api/cameras/feed`) возвращается поле `description_en` на английском языке (50–100 символов) для вычисления эмбеддингов в `transformers.js`.
- В `main.py` подключён `CORSMiddleware` для работы WebView Tauri по IP локальной сети.
- При старте и в `db/seed.py` выполняется автоматическая загрузка медиафайлов (`camera_1..4.jpg`, `video_1..4.mp4`) в MinIO.

## Запуск стенда
```bash
docker compose up -d postgres redis minio adminer
alembic upgrade head
python3 -m db.seed
uvicorn main:app --host 0.0.0.0 --port 8000
```

> Важно: указывайте `--host 0.0.0.0`, чтобы собранное приложение Tauri могло подключаться по IP ноутбука в локальной сети (`ipconfig getifaddr en0`), а не только по `localhost`.
