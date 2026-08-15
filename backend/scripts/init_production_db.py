"""Production database initializer for non-product startup data."""
from __future__ import annotations

import sys
from sqlalchemy import select, func

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

        print("Product seed and legacy smartphone synchronization are disabled.", flush=True)

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
