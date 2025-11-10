# Makefile for MMFOOD Development

.PHONY: help dev build test lint clean install

help:
	@echo "MMFOOD Development Commands:"
	@echo "  make install    - Install all dependencies"
	@echo "  make dev        - Start development servers"
	@echo "  make build      - Build all services"
	@echo "  make test       - Run all tests"
	@echo "  make lint       - Run linters"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make docker-up  - Start Docker services"
	@echo "  make docker-down - Stop Docker services"

install:
	@echo "Installing API dependencies..."
	cd app/api && pip install -r requirements.txt
	@echo "Installing Web dependencies..."
	cd app/web && npm install
	@echo "Installing shared types..."
	cd app/packages/types && npm install

dev:
	@echo "Starting development servers..."
	@echo "Run these in separate terminals:"
	@echo "  Terminal 1: cd app/api && python main.py"
	@echo "  Terminal 2: cd app/web && npm run dev"

build:
	@echo "Building shared types..."
	cd app/packages/types && npm run build
	@echo "Building web..."
	cd app/web && npm run build

test:
	@echo "Running API tests..."
	cd app/api && pytest
	@echo "Running Web tests..."
	cd app/web && npm test

lint:
	@echo "Linting API..."
	cd app/api && ruff check . && black --check .
	@echo "Linting Web..."
	cd app/web && npm run lint

clean:
	@echo "Cleaning build artifacts..."
	rm -rf app/web/.next
	rm -rf app/web/node_modules
	rm -rf app/packages/types/dist
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-up:
	cd app/infra && docker-compose up -d

docker-down:
	cd app/infra && docker-compose down

docker-logs:
	cd app/infra && docker-compose logs -f
