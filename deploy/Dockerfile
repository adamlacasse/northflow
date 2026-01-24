# Production image for NorthFlow (Flask) with gunicorn
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt pyproject.toml README.md /app/
COPY app /app/app
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy runtime config and deployment scripts
COPY config.py /app/
COPY deploy /app/deploy
RUN sed -i 's/\r$//' /app/deploy/entrypoint.sh /app/deploy/migrate.sh \
    && chmod +x /app/deploy/entrypoint.sh /app/deploy/migrate.sh

EXPOSE 8000

# Default to web entrypoint; can be overridden for migrations
ENTRYPOINT ["/app/deploy/entrypoint.sh"]
CMD ["web"]
