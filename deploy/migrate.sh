#!/bin/sh
set -e

# Apply database schema using the same image in a one-off ECS task
python -m app.database.setup_schema
