# SOFIA-S — Google Forms Data Aggregation Platform

A production-grade Django application for aggregating Google Forms responses via the Google Sheets API.

## Stack

| Layer | Technology |
|---|---|
| Framework | Django 6 |
| Database | SQLite (WAL mode, production-grade for read-heavy workloads) |
| Auth | Passwordless email (magic links, 15-min expiry) |
| Data source | Google Sheets API v4 via service account |
| API | Plain `JsonResponse` (3 endpoints, no DRF overhead) |
| Serving | Gunicorn (production), Django runserver (development) |
| Containerisation | Docker + docker-compose |

## Quick Start

```bash
# 1. Install dependencies
poetry install

# 2. Configure environment
cp .env.example .env
# Edit .env — set SECRET_KEY and GOOGLE_CREDENTIALS_FILE at minimum

# 3. Apply migrations
make migrate

# 4. Create a staff user (admin role)
poetry run python src/manage.py createsuperuser

# 5. Start the development server
make run
# → http://localhost:8000
```

## Common Commands

| Command | Description |
|---|---|
| `make run` | Start dev server |
| `make migrate` | Apply migrations |
| `make makemigrations` | Generate migration files |
| `make test` | Run test suite |
| `make lint` | Lint with ruff |
| `make format` | Format with ruff |
| `make typecheck` | Type-check with mypy |
| `make sync` | Sync all active Google Sheets |
| `make collectstatic` | Collect static files |
| `make docker-up` | Start Docker containers |
| `make docker-down` | Stop Docker containers |

## Key URLs

| Path | Description |
|---|---|
| `/login/` | Passwordless login (email magic link) |
| `/dashboard/` | Response overview with Chart.js chart |
| `/spreadsheets/` | List all configured spreadsheets |
| `/spreadsheets/<id>/` | View responses in a table |
| `/api/spreadsheets/` | JSON: list spreadsheets |
| `/api/spreadsheets/<id>/` | JSON: spreadsheet + responses |
| `/api/spreadsheets/<id>/?format=csv` | CSV download |
| `/api/dashboard/stats/` | JSON: aggregate statistics |
| `/health/` | Health check (`{"status": "ok"}`) |
| `/admin/` | Django admin (add spreadsheets, trigger sync) |

## Architecture

```
src/
├── config/settings/   base → development / production
├── core/              health check, @staff_required decorator
├── accounts/          passwordless auth (LoginToken model)
├── sheets/            Spreadsheet + FormResponse models, GoogleSheetsService
├── api/               3 JSON/CSV endpoints
├── templates/         Bootstrap 5 + Chart.js (CDN)
└── static/            custom.css, charts.js
```

## Google Sheets Setup

1. Create a Google Cloud project and enable the Sheets API.
2. Create a service account and download the JSON credentials file.
3. Share each target spreadsheet with the service account email (read-only).
4. Set `GOOGLE_CREDENTIALS_FILE=/path/to/credentials.json` in `.env`.
5. Add a `Spreadsheet` record via `/admin/` with the sheet's Google ID.
6. Run `make sync` or trigger the admin action to import responses.

## Production Deployment

```bash
# Build
docker build -t sofia-s .

# Run (supply env vars via your hosting platform)
docker run -e SECRET_KEY=... -e GOOGLE_CREDENTIALS_FILE=... -p 8000:8000 sofia-s
```

Set `DJANGO_SETTINGS_MODULE=config.settings.production` in production.
