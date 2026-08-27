set default-list := true

start-db:
	docker compose up -d 

stop-db:
	docker compose down -v

run-api:
	PYTHONPATH=src uv run fastapi dev src/cmd/api.py

run-evaluator:
	PYTHONPATH=src uv run python -m agent.evaluator
