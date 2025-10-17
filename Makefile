.PHONY: help up down logs postgres mysql clean

# Default target
help:
	@echo "ReleaseBot AI - Docker Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make up         - Start the application with PostgreSQL (default)"
	@echo "  make up-postgres- Start the application with PostgreSQL"
	@echo "  make up-mysql   - Start the application with MySQL"
	@echo "  make down       - Stop and remove containers"
	@echo "  make logs       - Show application logs"
	@echo "  make clean      - Remove all containers, volumes, and images"
	@echo ""
	@echo "Access the application:"
	@echo "  - FastAPI: http://localhost:8000"
	@echo "  - Streamlit UI: http://localhost:8501"
	@echo "  - API Docs: http://localhost:8000/docs"

# Start with PostgreSQL (default)
up: up-postgres

# Start with PostgreSQL
up-postgres:
	@echo "Starting ReleaseBot AI with PostgreSQL..."
	docker compose -f docker-compose.postgres.yml up -d
	@echo "Application is starting..."
	@echo "FastAPI: http://localhost:8000"
	@echo "Streamlit UI: http://localhost:8501"

# Start with MySQL
up-mysql:
	@echo "Starting ReleaseBot AI with MySQL..."
	docker compose -f docker-compose.mysql.yml up -d
	@echo "Application is starting..."
	@echo "FastAPI: http://localhost:8000"
	@echo "Streamlit UI: http://localhost:8501"

# Stop containers
down:
	@echo "Stopping ReleaseBot AI..."
	docker compose -f docker-compose.postgres.yml down
	docker compose -f docker-compose.mysql.yml down

# Show logs
logs:
	@if [ -f ".docker-db-type" ]; then \
		db_type=$$(cat .docker-db-type); \
		if [ "$$db_type" = "mysql" ]; then \
			docker compose -f docker-compose.mysql.yml logs -f; \
		else \
			docker compose -f docker-compose.postgres.yml logs -f; \
		fi; \
	else \
		docker compose -f docker-compose.postgres.yml logs -f; \
	fi

# Clean everything
clean:
	@echo "Removing all containers, volumes, and images..."
	docker compose -f docker-compose.postgres.yml down -v --rmi all
	docker compose -f docker-compose.mysql.yml down -v --rmi all
	docker system prune -f
	@echo "Cleanup complete!"

# Build image
build:
	@echo "Building ReleaseBot AI image..."
	docker compose -f docker-compose.postgres.yml build