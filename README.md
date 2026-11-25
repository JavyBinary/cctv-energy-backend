# Бэкенд: Расчет энергопотребления видеонаблюдения (Доп. задание: Индексы в БД)

Ветка: `indexes` (репозиторий `cctv-energy-backend`).

## Реализовано
1. **Составной индекс PostgreSQL** (`alembic/versions/a8c4e91f2b30_add_cameras_status_power_id_index.py`):
   `idx_cameras_status_power_id ON cameras (status, power, id)` — покрывает фильтрацию плитки по мощности и сортировку.
2. **Генерация 100 000 записей** (`db/seed_bulk.py`):
   Вставка одним SQL-запросом `generate_series`, очистка флагом `--clean`.
3. **Пагинация каталога** (`GET /api/cameras?power_max=&page=1&limit=12`):
   Ответ `{ total, page, limit, data }`.
4. **Лента в Redis** (`GET /api/cameras/feed/batch?session_id=&refresh=false`):
   Формирует и кэширует в Redis (`cameras:feed:<session_id>`, TTL 30 мин) 100 случайных неповторяющихся опубликованных камер со сквозными порядковыми номерами (`1..100`, `101..200`, ...).

## Команды запуска
```bash
make infra-up       # Поднять Postgres, Redis, MinIO, Adminer
make migrate-up     # Применить миграции (включая индекс)
make seed           # Базовые пользователи и 6 камер
make seed-bulk      # Добавить 100 000 камер
make run            # Запустить FastAPI на :8000
```

## Проверка индекса (`EXPLAIN ANALYZE`) и Redis
```sql
ANALYZE cameras;
EXPLAIN ANALYZE SELECT * FROM cameras WHERE status = 'published' AND power <= 4.0 ORDER BY power, id LIMIT 12 OFFSET 2000;
DROP INDEX idx_cameras_status_power_id;
EXPLAIN ANALYZE SELECT * FROM cameras WHERE status = 'published' AND power <= 4.0 ORDER BY power, id LIMIT 12 OFFSET 2000;
CREATE INDEX idx_cameras_status_power_id ON cameras (status, power, id);
```
```bash
docker exec -i redis_cache redis-cli --scan --pattern 'cameras:feed:*'
docker exec -i redis_cache redis-cli GET cameras:feed:<session_id>
```
