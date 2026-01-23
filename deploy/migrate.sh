#!/bin/sh
set -e

# Database migrations / schema application.
#
# IMPORTANT:
# - "schema" is DESTRUCTIVE (schema.sql contains DROP DATABASE) and is intended
#   for one-time bootstrap only.
# - "objects" is SAFE and repeatable (procedures/views/functions), and should
#   run on every deploy to prevent "missing routine" race conditions.
MODE=${MIGRATE_MODE:-objects}

if [ "$MODE" = "schema" ]; then
  python -m app.database.setup_schema
elif [ "$MODE" = "objects" ]; then
  python -m app.database.apply_schema_objects
else
  echo "Unknown migrate mode: $MODE" >&2
  exit 1
fi
