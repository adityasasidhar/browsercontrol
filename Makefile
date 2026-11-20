.DEFAULT_GOAL := help
.PHONY: help install browsers lint format typecheck security test cov docs check pre-commit

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

install: ## Install runtime and dev dependencies
	uv sync

browsers: ## Install the Playwright Chromium engine
	uv run playwright install chromium

lint: ## Ruff lint and format check
	uv run ruff check .
	uv run ruff format --check .

format: ## Autofix lint issues and format
	uv run ruff check . --fix
	uv run ruff format .

typecheck: ## mypy (strict)
	uv run mypy browsercontrol/

security: ## bandit security scan
	uv run bandit -c pyproject.toml -r . --exclude ./tests,./.venv

test: ## Run the test suite
	uv run pytest

cov: ## Run tests with coverage
	uv run pytest --cov=browsercontrol

docs: ## Build the docs site (strict)
	uv run --extra docs mkdocs build --strict

check: lint typecheck test ## Lint, type-check and test

pre-commit: ## Run every pre-commit hook
	uv run pre-commit run --all-files
