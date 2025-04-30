.DEFAULT_GOAL := help

install-req: ## install requirements with uv based on pyproject.toml / uv.lock
	uv sync

test: ## run tests
	uv run pytest -sv .

run: ## python run app
	docker compose up test-db -d
	make migrate-upgrade
	python utils/reset_db.py
	uvicorn main:app --reload

token:
	uv run utils/generate_token.py

fresh-run:
	docker compose down test-db people_api --remove-orphans
	docker compose up test-db -d
	@echo "Waiting for test-db to be ready..."
	@until docker exec mensa-api-test-db-1 pg_isready -U postgres >/dev/null 2>&1; do sleep 1; done
	@echo "Making migrations..."
	make migrate-upgrade
	@echo "Resetting database..."
	python utils/reset_db.py
	@echo "Killing any process using port 5000..."
	- fuser -k 5000/tcp || true
	@echo "Starting Api"
	uv run uvicorn people_api.app:app --reload --host 0.0.0.0 --port 5000

down:
	docker compose down

demo:
	docker compose down; docker compose build; docker compose up -d; make migrate-upgrade;

restart: ## restart app
	docker compose restart people_api

run-docker-background: ## start running through docker-compose, detached
	docker-compose up -d

teardown-docker: ## remove from docker through docker-compose
	docker-compose down

start-test-mongo: ## start mongodb in docker for tests
	docker run -d --rm --name=fastapi_mongodb_tests -p 27017:27017 --tmpfs=/data/db mongo

stop-test-mongo: ## stop dockerized mongodb for tests
	docker stop fastapi_mongodb_tests

pgadmin: ## start pgadmin in docker
	docker compose up pgadmin -d

migrate-autogenerate: ## generate migration using alembic autogenerate
	uv run alembic -c people_api/database/alembic.ini revision --autogenerate -m "$(m)"

migrate-upgrade: ## upgrade database using alembic (apply last generated migration)
	uv run alembic -c people_api/database/alembic.ini upgrade head

mypy: ## run mypy
	uv run mypy .

help: ## show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
