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

        print("Running production seed sync...", flush=True)

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

        # Always run smartphone sync to upsert latest models and affiliate URLs in production.
        print("  Syncing smartphone catalog (idempotent upsert)...", flush=True)
        from scripts.seed_smartphones import run as seed_phones  # type: ignore[import]
        seed_phones()

        print("  Syncing verified Apple iPhone SKUs...", flush=True)
        from scripts.sync_verified_apple_iphones import run as sync_verified_iphones  # type: ignore[import]
        sync_verified_iphones()

        if article_count == 0:
            print("  Seeding launch articles...", flush=True)
            from scripts.seed_articles import run as seed_articles  # type: ignore[import]
            seed_articles()
            final_articles = db.execute(select(func.count()).select_from(Article)).scalar() or 0
            print(f"Articles seeded: {final_articles}", flush=True)

        smartphone_count = db.execute(
            text("""
                SELECT COUNT(*)
                FROM products p
                JOIN categories c ON c.id = p.category_id
                WHERE c.slug IN ('phone', 'smartphones')
            """)
        ).scalar() or 0
        apple_count = db.execute(
            text("""
                SELECT COUNT(*)
                FROM products p
                JOIN brands b ON b.id = p.brand_id
                WHERE b.name = 'Apple'
            """)
        ).scalar() or 0
        print(f"Smartphone products: {smartphone_count}", flush=True)
        print(f"Apple products: {apple_count}", flush=True)

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
