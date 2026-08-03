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

echo "STEP 3: Checking product catalog..."
PRODUCT_COUNT=$(python -c "
from app.db.session import SessionLocal
from sqlalchemy import text
db = SessionLocal()
count = db.execute(text('SELECT COUNT(*) FROM products')).scalar()
db.close()
print(count)
")
echo "STEP 3: Products in database: $PRODUCT_COUNT"

if [ "$PRODUCT_COUNT" = "0" ]; then
  echo "STEP 3a: Database empty — seeding base catalog (300 products)..."
  python -m scripts.seed_products
  echo "STEP 3b: Seeding smartphone catalog (121 products)..."
  python -m scripts.seed_smartphones
  echo "STEP 3: Seeding complete."
else
  echo "STEP 3: Catalog already populated ($PRODUCT_COUNT products), skipping seed."
fi

echo "STEP 4: Starting Uvicorn on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
