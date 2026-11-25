.PHONY: infra-up infra-down migrate-up migrate-down seed seed-bulk seed-clean run redis-feed explain

infra-up:
	docker compose up -d postgres redis minio adminer

infra-down:
	docker compose stop postgres redis minio adminer

migrate-up:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

seed:
	python3 -m db.seed

seed-bulk:
	python3 -m db.seed_bulk --count 100000

seed-clean:
	python3 -m db.seed_bulk --clean

run:
	uvicorn main:app --reload --port 8000

redis-feed:
	docker exec -i redis_cache redis-cli --scan --pattern 'cameras:feed:*'

explain:
	docker exec -i postgres_db psql -U camera_user -d cameras_db -c "ANALYZE cameras; EXPLAIN ANALYZE SELECT * FROM cameras WHERE status = 'published' AND power <= 4.0 ORDER BY power, id LIMIT 12 OFFSET 2000;"
