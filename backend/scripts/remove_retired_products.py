"""Remove the two accidentally imported household products from the catalog.

Usage:
  python -m scripts.remove_retired_products
  python -m scripts.remove_retired_products --confirm

The default mode is a dry run. This script only targets the two exact product
names listed below and never deletes orders or users.
"""
from __future__ import annotations

import argparse
import sys

from sqlalchemy import func, select

sys.path.insert(0, ".")

from app.db.session import SessionLocal
from app.models.entities import CartItem, OrderItem, Product


TARGET_NAMES = {
    "60CM Sewer Dredger Spring Pipe Dredging Tool Household Hair Cleaner Drain Clog Remover Cleaning Tools Household For Kitchen Sink Kitchen Gadgets",
    "Creative Swordfish Handle Metal Beer Bottle Openers Kitchen Bar Accessories Tools Beer Gifts Beer Openors Kitchen Gadgets for Kitchen and Bar Use",
}


def normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def find_targets(db) -> list[Product]:
    target_names = {normalized(name) for name in TARGET_NAMES}
    products = list(db.scalars(select(Product)).all())
    return [product for product in products if normalized(product.name) in target_names]


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove retired imported products")
    parser.add_argument("--confirm", action="store_true", help="Delete matched products after blocker checks")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        products = find_targets(db)
        print(f"Matched products: {len(products)}")
        if not products:
            print("Nothing to remove.")
            return

        blocked = False
        for product in products:
            order_count = db.scalar(select(func.count()).select_from(OrderItem).where(OrderItem.product_id == product.id)) or 0
            cart_count = db.scalar(select(func.count()).select_from(CartItem).where(CartItem.product_id == product.id)) or 0
            print(f"- {product.id} [{product.status}] {product.name}")
            print(f"  order items: {order_count}; cart items: {cart_count}")
            if order_count or cart_count:
                blocked = True

        if blocked:
            raise SystemExit("Removal stopped: matched products have order or cart references.")
        if not args.confirm:
            print("Dry run only. Re-run with --confirm to permanently remove these products.")
            return

        for product in products:
            db.delete(product)
        db.commit()
        print(f"Removed products: {len(products)}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
