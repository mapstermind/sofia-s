.PHONY: help install run migrate makemigrations test lint format typecheck shell \
        sync collectstatic docker-up docker-down docker-build

MANAGE := src/manage.py

help:
	@echo ""
	@echo "SOFIA-S — available make targets"
	@echo "---------------------------------"
	@echo "  install          Install dependencies (poetry install)"
	@echo "  run              Start Django development server"
	@echo "  migrate          Apply database migrations"
	@echo "  makemigrations   Generate new migration files"
	@echo "  test             Run the test suite (pytest)"
	@echo "  lint             Lint with ruff"
	@echo "  format           Format with ruff"
	@echo "  typecheck        Type-check with mypy"
	@echo "  shell            Open Django interactive shell"
	@echo "  sync             Sync all active spreadsheets from Google Sheets"
	@echo "  collectstatic    Collect static files"
	@echo "  docker-build     Build Docker image"
	@echo "  docker-up        Start containers (docker-compose up -d)"
	@echo "  docker-down      Stop containers (docker-compose down)"
	@echo ""

install:
	poetry install

run:
	poetry run python $(MANAGE) runserver

migrate:
	poetry run python $(MANAGE) migrate

makemigrations:
	poetry run python $(MANAGE) makemigrations

test:
	poetry run pytest

lint:
	poetry run ruff check src/

format:
	poetry run ruff format src/

typecheck:
	poetry run mypy src/

shell:
	poetry run python $(MANAGE) shell

sync:
	poetry run python $(MANAGE) sync_sheets --all

collectstatic:
	poetry run python $(MANAGE) collectstatic --noinput

docker-build:
	docker build -t sofia-s .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
