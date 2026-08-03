"""
Admin Product Import Script
============================
Import products from a JSON or CSV file into the database.

Usage:
  python -m scripts.import_products --file products.json
  python -m scripts.import_products --file products.csv --format csv

JSON format (list of objects):
[
  {
    "brand": "Hostinger",
    "name": "Hostinger Business Plan",
    "category_slug": "web-hosting",
    "price": 179,
    "rating": 4.8,
    "ai_score": 96,
    "description": "...",
    "buy_links": [{"label": "Official Site", "href": "https://hostinger.in/...", "retailer_type": "official"}],
    "specs": [{"label": "Storage", "value": "200 GB SSD"}],
    "pros": ["Fast performance"],
    "cons": ["No phone support"],
    "best_for": ["small businesses"],
    "not_for": ["enterprise"],
    "tags": ["hosting", "web-hosting"],
    "image_url": "https://..."
  }
]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, ".")

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.entities import (
    Brand, Category, Product, ProductBestFor, ProductBuyLink,
    ProductCon, ProductFeature, ProductImage, ProductNotRecommendedFor,
    ProductPro, ProductSpecification, ProductTag,
)


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"(^-|-$)", "", value)


def get_or_create_brand(db, name: str) -> Brand:
    existing = db.scalars(select(Brand).where(Brand.name == name)).first()
    if existing:
        return existing
    b = Brand(name=name, slug=slugify(name))
    db.add(b)
    db.flush()
    return b


def get_or_create_category(db, slug: str) -> Category | None:
    return db.scalars(select(Category).where(Category.slug == slug)).first()


def import_product(db, data: dict) -> str:
    brand = get_or_create_brand(db, data["brand"])
    category = get_or_create_category(db, data["category_slug"])
    if not category:
        return f"SKIP: category '{data['category_slug']}' not found"

    slug = slugify(f"{data['brand']}-{data['name']}")
    existing = db.scalars(select(Product).where(Product.slug == slug)).first()
    if existing:
        return f"SKIP: product '{slug}' already exists"

    product = Product(
        slug=slug,
        name=data["name"],
        description=data.get("description", f"{data['name']} by {data['brand']}"),
        availability=data.get("availability", "In Stock"),
        category_id=category.id,
        brand_id=brand.id,
        price_value=Decimal(str(data["price"])),
        currency=data.get("currency", "INR"),
        rating=Decimal(str(data["rating"])),
        ai_score=int(data["ai_score"]),
        ai_summary=data.get("ai_summary", f"{data['name']} scores {data['ai_score']}/100 by LeTrusto AI."),
        review_summary=data.get("review_summary", ""),
        series=data.get("series"),
        model_name=data.get("model_name"),
        variant=data.get("variant"),
        storage=data.get("storage"),
        ram=data.get("ram"),
        color=data.get("color"),
    )
    db.add(product)
    db.flush()

    if data.get("image_url"):
        db.add(ProductImage(product_id=product.id, url=data["image_url"], position=1))

    for pos, spec in enumerate(data.get("specs", []), start=1):
        db.add(ProductSpecification(product_id=product.id, label=spec["label"], value=spec["value"], position=pos))

    for pos, pro in enumerate(data.get("pros", []), start=1):
        db.add(ProductPro(product_id=product.id, value=pro, position=pos))

    for pos, con in enumerate(data.get("cons", []), start=1):
        db.add(ProductCon(product_id=product.id, value=con, position=pos))

    for pos, bf in enumerate(data.get("best_for", []), start=1):
        db.add(ProductBestFor(product_id=product.id, value=bf, position=pos))

    for pos, nf in enumerate(data.get("not_for", []), start=1):
        db.add(ProductNotRecommendedFor(product_id=product.id, value=nf, position=pos))

    for feat in data.get("features", []):
        db.add(ProductFeature(product_id=product.id, value=feat, position=1))

    for tag in {category.slug, slugify(data["brand"]), *data.get("tags", [])}:
        db.add(ProductTag(product_id=product.id, value=tag))

    for link_data in data.get("buy_links", []):
        db.add(ProductBuyLink(
            product_id=product.id,
            label=link_data["label"],
            href=link_data["href"],
            retailer_type=link_data.get("retailer_type", "marketplace"),
            is_affiliate=link_data.get("is_affiliate", True),
        ))

    return f"OK: created '{slug}'"


def main() -> None:
    parser = argparse.ArgumentParser(description="Import products from JSON or CSV")
    parser.add_argument("--file", required=True, help="Path to import file")
    parser.add_argument("--format", default="json", choices=["json", "csv"])
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: File not found: {path}")
        sys.exit(1)

    if args.format == "json":
        with open(path, encoding="utf-8") as f:
            products = json.load(f)
    else:
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            products = list(reader)

    db = SessionLocal()
    inserted = 0
    skipped = 0
    errors = 0

    try:
        for p in products:
            result = import_product(db, p)
            print(result)
            if result.startswith("OK"):
                inserted += 1
            elif result.startswith("SKIP"):
                skipped += 1
            else:
                errors += 1
        db.commit()
        print(f"\nDone. Inserted: {inserted} | Skipped: {skipped} | Errors: {errors}")
    except Exception as e:
        db.rollback()
        print(f"FATAL: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
