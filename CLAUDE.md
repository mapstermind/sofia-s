# CLAUDE.md — AI Assistant Guide for SOFIA-S

## Project Overview

SOFIA-S is a Django 6 application that pulls Google Forms responses via the Sheets API and presents them through a staff-only web UI and three JSON/CSV API endpoints. Users authenticate via passwordless magic links.

## Running the Project

```bash
poetry install        # Install deps
make migrate          # Apply migrations
make run              # Start dev server at http://localhost:8000
make test             # Run pytest
make lint             # ruff check
make typecheck        # mypy
```

## Architecture at a Glance

- **`src/config/settings/`** — split settings: `base.py` → `development.py` / `production.py`
- **`src/core/`** — `health_check` view, `@staff_required` decorator, WAL mode signal
- **`src/accounts/`** — `LoginToken` model, magic-link views, email helper
- **`src/sheets/`** — `Spreadsheet` + `FormResponse` models, lazy `GoogleSheetsService`, management command
- **`src/api/`** — `SpreadsheetListView`, `SpreadsheetDetailView` (JSON+CSV), `DashboardStatsView`
- **`src/templates/`** — Bootstrap 5 + Chart.js (all via CDN), no build step
- **`src/static/`** — `custom.css`, `charts.js`

## Critical Gotchas

1. **`BASE_DIR`** in `config/settings/base.py` goes 3 parents up (reaches `src/`), not 2.
2. All three entry points (`manage.py`, `wsgi.py`, `asgi.py`) default to `config.settings.development`.
3. `GoogleSheetsService._get_service()` is **lazy** — it only builds the Google API client on first call, so it can be instantiated in tests without credentials.
4. Chart.js data in templates: always pass as `json.dumps(..., cls=DjangoJSONEncoder)` and render with `{{ chart_data_json|safe }}` inside `<script>` tags.
5. `LoginToken.token` is 64 characters: `secrets.token_urlsafe(48)` → base64 output.
6. All UI views and API endpoints require `is_staff=True` (via `@staff_required` decorator or `StaffRequiredMixin`).
7. SQLite WAL mode is enabled automatically via a `connection_created` signal in `core/apps.py`.

## Testing Strategy

- Use `unittest.mock.patch.object(service, "get_sheet_data", ...)` to test `GoogleSheetsService` without real credentials.
- Use `client.force_login(user)` in API tests.
- The console email backend in development captures emails to stdout; `mailoutbox` fixture in pytest-django captures them in tests.

## Adding a New Spreadsheet

1. Go to `/admin/sheets/spreadsheet/add/`
2. Enter the Google Spreadsheet ID (from the URL) and the tab name
3. Run `make sync` or use the admin "Sync" action

## Dependencies

Managed with Poetry. Key packages: `django>=6.0`, `google-api-python-client`, `google-auth`, `python-dotenv`, `gunicorn`. Dev: `pytest-django`, `ruff`, `mypy`, `django-stubs`.
