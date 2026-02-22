.PHONY: help install run migrate makemigrations test lint format typecheck shell

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies using poetry"
	@echo "  run          - Run Django development server"
	@echo "  migrate      - Run Django migrations"
	@echo "  makemigrations - Create new Django migrations"
	@echo "  test         - Run tests using pytest"
	@echo "  lint         - Run ruff linter"
	@echo "  format       - Run ruff formatter"
	@echo "  typecheck    - Run mypy type checker"
	@echo "  shell        - Open Django shell"
	@echo "  help         - Show this help message"

# Path to manage.py (can be overridden if needed)
MANAGE := src/manage.py

# Install dependencies
install:
	poetry install

# Run Django development server
run:
	poetry run python $(MANAGE) runserver

# Run migrations
migrate:
	poetry run python $(MANAGE) migrate

# Create migrations
makemigrations:
	poetry run python $(MANAGE) makemigrations

# Run tests
test:
	poetry run pytest

# Run linter
lint:
	poetry run ruff check

# Run formatter
format:
	poetry run ruff format

# Run type checker
typecheck:
	poetry run mypy

# Open Django shell
shell:
	poetry run python $(MANAGE) shell
