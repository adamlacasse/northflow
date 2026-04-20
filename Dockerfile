FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies (gcc for any native builds) and cleanup to keep image small
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first to leverage Docker layer caching
# Copy metadata and package source so editable install (-e .) works
COPY requirements.txt pyproject.toml README.md /app/
COPY app /app/app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Ensure deploy scripts are executable (cross-platform safety)
RUN chmod +x /app/deploy/entrypoint.sh /app/deploy/migrate.sh

EXPOSE 8000

# Production entrypoint: applies idempotent schema objects, then execs gunicorn.
# To run the destructive one-time schema bootstrap instead, override the
# command with: /app/deploy/entrypoint.sh migrate (with MIGRATE_MODE=schema).
CMD ["/app/deploy/entrypoint.sh"]
