.PHONY: help up up-postgres up-mysql down logs clean build

COMPOSE_POSTGRES = infra/docker-compose.postgres.yml
COMPOSE_MYSQL = infra/docker-compose.mysql.yml

help:
	@echo "ReleaseBot AI - Development Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make up           Start with PostgreSQL (default)"
	@echo "  make up-postgres  Start with PostgreSQL"
	@echo "  make up-mysql     Start with MySQL"
	@echo "  make down         Stop containers"
	@echo "  make logs         Tail PostgreSQL stack logs"
	@echo "  make build        Build app image"
	@echo "  make clean        Remove containers, volumes, and dangling resources"

up: up-postgres

up-postgres:
	@echo "Starting ReleaseBot AI with PostgreSQL..."
	docker compose -f $(COMPOSE_POSTGRES) up -d
	@echo "FastAPI: http://localhost:8000"
	@echo "Streamlit: http://localhost:8501"

up-mysql:
	@echo "Starting ReleaseBot AI with MySQL..."
	docker compose -f $(COMPOSE_MYSQL) up -d
	@echo "FastAPI: http://localhost:8000"
	@echo "Streamlit: http://localhost:8501"

down:
	@echo "Stopping ReleaseBot AI containers..."
	docker compose -f $(COMPOSE_POSTGRES) down
	docker compose -f $(COMPOSE_MYSQL) down

logs:
	docker compose -f $(COMPOSE_POSTGRES) logs -f

build:
	@echo "Building ReleaseBot AI image..."
	docker compose -f $(COMPOSE_POSTGRES) build

clean:
	@echo "Removing containers, volumes, and dangling resources..."
	docker compose -f $(COMPOSE_POSTGRES) down -v --rmi local
	docker compose -f $(COMPOSE_MYSQL) down -v --rmi local
	docker system prune -f
