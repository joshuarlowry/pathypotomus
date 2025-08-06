.PHONY: help install install-dev test test-cov lint format clean docker-build docker-up docker-down setup

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# Setup and installation
setup: ## Set up development environment
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source venv/bin/activate  # Linux/Mac"
	@echo "  venv\\Scripts\\activate     # Windows"

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt
	pre-commit install

# Development environment
dev-env: ## Copy .env.example to .env.dev for development
	cp .env.example .env.dev
	@echo "Development environment file created: .env.dev"
	@echo "Please edit .env.dev with your configuration"

# Testing
test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage report
	pytest tests/ -v --cov=src/pathypotomus --cov-report=html --cov-report=term

test-unit: ## Run only unit tests
	pytest tests/unit/ -v

test-integration: ## Run only integration tests
	pytest tests/integration/ -v -m integration

# Code quality
lint: ## Run linting checks
	flake8 src/ tests/
	mypy src/
	black --check src/ tests/
	isort --check-only src/ tests/

format: ## Format code
	black src/ tests/
	isort src/ tests/

# Cleaning
clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

# Docker
docker-build: ## Build Docker image
	docker-compose build

docker-up: ## Start services with Docker Compose
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

# Application
run: ## Run the application
	python src/pathypotomus/main.py

run-dev: ## Run the application in development mode
	PYTHONPATH=src python src/pathypotomus/main.py --config .env.dev

# Project structure
tree: ## Show project structure
	@echo "Project structure:"
	@find . -type f -name "*.py" | head -20 | sort