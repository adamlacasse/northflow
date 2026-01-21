#!/usr/bin/env sh
set -e

MODE=${1:-web}
shift || true

if [ "$MODE" = "web" ]; then
  exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 60 "app:create_app()"
elif [ "$MODE" = "migrate" ]; then
  exec /app/deploy/migrate.sh "$@"
else
  echo "Unknown mode: $MODE" >&2
  exit 1
fi
