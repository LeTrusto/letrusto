#!/bin/sh
set -e

echo "========================================"
echo "STEP 1: LeTrusto backend starting"
echo "  PYTHONPATH=$PYTHONPATH"
echo "  PORT=${PORT:-8000}"
echo "  APP_ENV=${APP_ENV:-not set}"
echo "  DATABASE_URL set: $([ -n "$DATABASE_URL" ] && echo YES || echo NO)"
echo "========================================"

echo "STEP 2: Running Alembic migrations..."
alembic upgrade head
echo "STEP 2: Alembic migrations complete."

echo "STEP 3: Starting Uvicorn on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
