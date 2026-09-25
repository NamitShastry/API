.PHONY: help setup dev test seed simulate migrate lint clean docker-up docker-down

help:
	@echo "AeroIndex / FareOS — Available Commands"
	@echo "=========================================="
	@echo "  make setup       Install API and Web dependencies"
	@echo "  make dev         Run API backend and Web frontend concurrently"
	@echo "  make api         Run FastAPI backend server"
	@echo "  make web         Run Next.js frontend development server"
	@echo "  make migrate     Run database migrations"
	@echo "  make seed        Seed reference data (routes, buckets, sources, weights)"
	@echo "  make simulate    Start the continuous observation simulator"
	@echo "  make test        Run all test suites (unit, contract, integration)"
	@echo "  make lint        Lint backend and frontend code"
	@echo "  make docker-up   Start all Docker services"
	@echo "  make docker-down Stop all Docker services"
	@echo "  make clean       Remove temporary files and caches"

setup:
	@echo "Installing backend dependencies..."
	python3 -m pip install -r services/api/requirements.txt
	@echo "Installing frontend dependencies..."
	cd services/web && npm install

dev:
	@echo "Starting development environment..."
	./scripts/dev.sh

api:
	@echo "Starting FastAPI backend on port 8000..."
	cd services/api && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

web:
	@echo "Starting Next.js frontend on port 3000..."
	cd services/web && npm run dev

migrate:
	@echo "Running database migrations..."
	cd services/api && alembic upgrade head

seed:
	@echo "Seeding reference and calibration data..."
	cd services/api && python3 -m app.seeds.seed_all

simulate:
	@echo "Starting continuous live observation simulator..."
	cd services/api && python3 -m app.collector.simulator --continuous

test:
	@echo "Running tests..."
	cd services/api && pytest tests/ -v

lint:
	@echo "Running linters..."
	cd services/api && ruff check . || true
	cd services/web && npm run lint || true

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".next" -exec rm -rf {} +
