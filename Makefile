run:
	uvicorn main:app --reload --port 8000

migrate:
	alembic upgrade head

seed:
	python3 -m db.seed