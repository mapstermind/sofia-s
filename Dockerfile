# Production image — python:3.12-slim + poetry + gunicorn
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME=/opt/poetry \
    DJANGO_SETTINGS_MODULE=config.settings.production

ENV PATH="$POETRY_HOME/bin:$PATH"

# System deps (curl for Poetry installer, build-essential for C extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry (pinned for reproducible builds)
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# Copy lockfile first to maximise layer caching
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-ansi

# Copy application source
COPY . .

# Collect static assets
RUN poetry run python src/manage.py collectstatic --noinput

EXPOSE 8000

# gunicorn.conf.py sets chdir=/app/src and binds 0.0.0.0:8000
CMD ["gunicorn", "--config", "gunicorn.conf.py", "config.wsgi:application"]
