"""
Production database initializer — run automatically on startup.
Seeds the catalog only when the products table is empty (idempotent).
"""
from __future__ import annotations

import sys
from sqlalchemy import select, func, text

sys.path.insert(0, ".")

from app.db.session import SessionLocal
from app.models.entities import Product, Article


def main() -> None:
    db = SessionLocal()
    try:
        product_count = db.execute(select(func.count()).select_from(Product)).scalar() or 0
        article_count = db.execute(select(func.count()).select_from(Article)).scalar() or 0
        print(f"================================", flush=True)
        print(f"Products in DB: {product_count}", flush=True)
        print(f"Articles in DB: {article_count}", flush=True)

        if product_count > 0 and article_count > 0:
            print(f"Catalog fully populated. Skipping seed.", flush=True)
            print(f"================================", flush=True)
            return

        print("Running production seed...", flush=True)

        if product_count == 0:
            # Seed 1: base electronics catalog (300 products across 10 categories)
            print("  [1/3] Seeding base catalog...", flush=True)
            from scripts.seed_products import seed as seed_base  # type: ignore[import]
            seed_base()

            # Seed 2: real smartphone catalog (121 SKUs across 11 brands)
            print("  [2/3] Seeding smartphone catalog...", flush=True)
            from scripts.seed_smartphones import run as seed_phones  # type: ignore[import]
            seed_phones()

            # Seed 3: hosting & SaaS catalog (10 products)
            print("  [3/3] Seeding hosting & SaaS catalog...", flush=True)
            from scripts.seed_hosting_saas import run as seed_hosting  # type: ignore[import]
            seed_hosting()

            final = db.execute(select(func.count()).select_from(Product)).scalar() or 0
            print(f"Products seeded: {final}", flush=True)

        if article_count == 0:
            print("  Seeding launch articles...", flush=True)
            from scripts.seed_articles import run as seed_articles  # type: ignore[import]
            seed_articles()
            final_articles = db.execute(select(func.count()).select_from(Article)).scalar() or 0
            print(f"Articles seeded: {final_articles}", flush=True)

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
