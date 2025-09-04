# Claude Parser Development Makefile
# Provides shortcuts for common development tasks

.PHONY: help install test test-local-ci ci-info ci-clean lint format check push-safe

# Default target
help: ## Show this help message
	@echo "Claude Parser Development Commands"
	@echo "=================================="
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies with Poetry
	pip install poetry
	poetry install

test: ## Run tests locally
	poetry run pytest -v --tb=short

test-all: ## Run all tests including integration
	poetry run pytest tests/ -v --tb=short

test-local-ci: ## Run GitHub Actions locally using act
	@echo "🚀 Running GitHub Actions locally..."
	./scripts/test-local-ci.sh ci

ci-info: ## Show local CI information
	./scripts/test-local-ci.sh info

ci-clean: ## Clean local CI cache and artifacts
	./scripts/test-local-ci.sh clean

lint: ## Run linting
	poetry run ruff check .

format: ## Format code
	poetry run ruff format .

check: ## Run all quality checks
	poetry run ruff check .
	poetry run ruff format --check .
	poetry run pytest --cov=claude_parser --cov-report=term-missing

push-safe: ## Test locally then push to remote (recommended)
	@echo "🔍 Testing locally before push..."
	@make test-local-ci
	@echo "✅ Local tests passed!"
	@echo "🚀 Pushing to remote..."
	git push

install-push-hook: ## Install pre-push hook for automatic local CI testing
	@cp .pre-push .git/hooks/pre-push
	@chmod +x .git/hooks/pre-push
	@echo "✅ Pre-push hook installed"

clean: ## Clean up build artifacts and caches
	rm -rf build/ dist/ *.egg-info/ .coverage htmlcov/ .pytest_cache/
	find . -type d -name __pycache__ -delete
