.PHONY: start-db stop-db run-api

start-db:
	docker compose up -d 

stop-db:
	docker compose down -v

run-api:
	PYTHONPATH=src uv run fastapi dev src/cmd/api.py
