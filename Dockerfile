FROM python:3.11-slim-bookworm@sha256:6c2a1d2e3f4e5b6a7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a

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

EXPOSE 5000

# Default command; bind host/port already handled in run.py
CMD ["python", "run.py"]
