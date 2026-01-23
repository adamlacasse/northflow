#!/bin/sh
set -e

# Apply database schema using the same image in a one-off ECS task
MODE=${MIGRATE_MODE:-schema}

if [ "$MODE" = "schema" ]; then
  python -m app.database.setup_schema
elif [ "$MODE" = "objects" ]; then
  python -m app.database.apply_schema_objects
else
  echo "Unknown migrate mode: $MODE" >&2
  exit 1
fi
