"""
Production database initializer — run automatically on startup.
Seeds the catalog only when the products table is empty (idempotent).
"""
from __future__ import annotations

import sys
from sqlalchemy import select, func, text

sys.path.insert(0, ".")

from app.db.session import SessionLocal
from app.models.entities import Product


def main() -> None:
    db = SessionLocal()
    try:
        count = db.execute(select(func.count()).select_from(Product)).scalar() or 0
        print(f"================================", flush=True)
        print(f"Products in DB: {count}", flush=True)

        if count > 0:
            print(f"Skipping seed — catalog already populated.", flush=True)
            print(f"================================", flush=True)
            return

        print("Running production seed...", flush=True)

        # Seed 1: base electronics catalog (300 products across 10 categories)
        print("  [1/2] Seeding base catalog...", flush=True)
        from scripts.seed_products import seed as seed_base  # type: ignore[import]
        seed_base()

        # Seed 2: real smartphone catalog (121 SKUs across 11 brands)
        print("  [2/2] Seeding smartphone catalog...", flush=True)
        from scripts.seed_smartphones import run as seed_phones  # type: ignore[import]
        seed_phones()

        # Verify final count
        final = db.execute(select(func.count()).select_from(Product)).scalar() or 0
        print(f"Seed complete. Products now in DB: {final}", flush=True)
        print(f"================================", flush=True)

    except Exception as exc:
        import traceback
        traceback.print_exc()
        print(f"ERROR during seeding: {exc}", flush=True)
        print("Continuing startup — app will serve empty catalog.", flush=True)
    finally:
        db.close()


if __name__ == "__main__":
    main()
