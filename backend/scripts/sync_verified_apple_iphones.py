from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select

sys.path.insert(0, ".")

from app.db.session import SessionLocal
from app.models.entities import (
    Brand,
    Category,
    PriceHistory,
    Product,
    ProductBestFor,
    ProductCon,
    ProductFeature,
    ProductImage,
    ProductNotRecommendedFor,
    ProductPro,
    ProductSpecification,
    ProductTag,
    Review,
)


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"(^-|-$)", "", value)


def inr(amount: int) -> Decimal:
    return Decimal(str(amount))


@dataclass
class VerifiedPhone:
    slug: str
    name: str
    series: str
    model_name: str
    storage: str
    ram: str
    color: str
    price_inr: int
    rating: float
    ai_score: int
    display: str
    chip: str
    camera: str
    battery: str
    affiliate_url: str
    image_url: str
    pros: list[str]
    cons: list[str]
    best_for: list[str]
    not_for: list[str]
    tags: list[str]


VERIFIED_NEW_PHONES: list[VerifiedPhone] = [
    VerifiedPhone(
        slug="apple-iphone-17-256gb",
        name="iPhone 17 256GB",
        series="iPhone 17 Series",
        model_name="iPhone 17",
        storage="256GB",
        ram="8GB",
        color="Black",
        price_inr=89900,
        rating=4.8,
        ai_score=95,
        display='6.3" Super Retina XDR OLED, 1-120Hz ProMotion',
        chip="Apple A19",
        camera="48MP main + 12MP ultrawide",
        battery="3600mAh, 25W wired + MagSafe",
        affiliate_url="https://link.amazon/B0hZkkcht",
        image_url="/images/products/iphone16pro-1.svg",
        pros=["Bright 120Hz display", "Balanced flagship value", "A19 performance"],
        cons=["No telephoto lens", "Still expensive", "No charger included"],
        best_for=["everyday iOS users", "compact flagship buyers", "Apple ecosystem"],
        not_for=["telephoto photography", "budget shoppers"],
        tags=["iphone", "apple", "flagship", "5g", "ios", "compact", "smartphone"],
    ),
    VerifiedPhone(
        slug="apple-iphone-17-pro-512gb",
        name="iPhone 17 Pro 512GB",
        series="iPhone 17 Series",
        model_name="iPhone 17 Pro",
        storage="512GB",
        ram="12GB",
        color="Silver",
        price_inr=149900,
        rating=4.9,
        ai_score=97,
        display='6.3" Super Retina XDR OLED, 1-120Hz ProMotion',
        chip="Apple A19 Pro",
        camera="48MP main + 48MP ultrawide + 12MP 5× telephoto",
        battery="4450mAh, 35W wired + 25W MagSafe",
        affiliate_url="https://link.amazon/B0dJ0ewY4",
        image_url="/images/products/iphone16pro-1.svg",
        pros=["A19 Pro chip performance", "Excellent Pro camera system", "Compact premium body"],
        cons=["Very expensive", "No charger included", "Storage tier costs more"],
        best_for=["professional photography", "power users", "iOS ecosystem"],
        not_for=["budget buyers", "Android users"],
        tags=["iphone", "apple", "flagship", "5g", "camera", "ios", "pro"],
    ),
    VerifiedPhone(
        slug="apple-iphone-17-pro-max-256gb",
        name="iPhone 17 Pro Max 256GB",
        series="iPhone 17 Series",
        model_name="iPhone 17 Pro Max",
        storage="256GB",
        ram="12GB",
        color="Silver",
        price_inr=164900,
        rating=4.9,
        ai_score=98,
        display='6.9" Super Retina XDR OLED, 1-120Hz ProMotion',
        chip="Apple A19 Pro",
        camera="48MP main + 48MP ultrawide + 12MP 5× telephoto",
        battery="5000mAh, 35W wired + 25W MagSafe",
        affiliate_url="https://link.amazon/B01FUEr1a",
        image_url="/images/products/iphone16pro-1.svg",
        pros=["Best-in-class iPhone camera system", "Huge Pro display", "A19 Pro performance"],
        cons=["Very expensive", "Heavy at 230g", "No charger in box"],
        best_for=["professional photography", "videography", "power users"],
        not_for=["budget buyers", "small-phone lovers"],
        tags=["iphone", "apple", "flagship", "5g", "camera", "ios", "pro", "promax"],
    ),
    VerifiedPhone(
        slug="apple-iphone-air-256gb-light-gold",
        name="iPhone Air 256GB",
        series="iPhone Air Series",
        model_name="iPhone Air",
        storage="256GB",
        ram="12GB",
        color="Light Gold",
        price_inr=109900,
        rating=4.8,
        ai_score=96,
        display='6.6" Super Retina XDR OLED, 1-120Hz ProMotion',
        chip="Apple A19",
        camera="48MP main + 12MP ultrawide",
        battery="3650mAh, 30W wired + MagSafe",
        affiliate_url="https://link.amazon/B0bh5bPFq",
        image_url="/images/products/iphone16pro-1.svg",
        pros=["Ultra-thin premium design", "Lightweight in hand", "Large bright display"],
        cons=["No telephoto lens", "Premium pricing", "Sleek build needs a case"],
        best_for=["style-first buyers", "large-screen lovers", "everyday iOS use"],
        not_for=["camera enthusiasts", "budget buyers"],
        tags=["iphone", "apple", "air", "5g", "ios", "thin", "smartphone"],
    ),
    VerifiedPhone(
        slug="apple-iphone-air-256gb-cloud-white",
        name="iPhone Air 256GB",
        series="iPhone Air Series",
        model_name="iPhone Air",
        storage="256GB",
        ram="12GB",
        color="Cloud White",
        price_inr=109900,
        rating=4.8,
        ai_score=96,
        display='6.6" Super Retina XDR OLED, 1-120Hz ProMotion',
        chip="Apple A19",
        camera="48MP main + 12MP ultrawide",
        battery="3650mAh, 30W wired + MagSafe",
        affiliate_url="https://link.amazon/B0iWzgMLe",
        image_url="/images/products/iphone16pro-1.svg",
        pros=["Ultra-thin premium design", "Lightweight in hand", "Large bright display"],
        cons=["No telephoto lens", "Premium pricing", "Sleek build needs a case"],
        best_for=["style-first buyers", "large-screen lovers", "everyday iOS use"],
        not_for=["camera enthusiasts", "budget buyers"],
        tags=["iphone", "apple", "air", "5g", "ios", "thin", "smartphone"],
    ),
    VerifiedPhone(
        slug="apple-iphone-16e-128gb",
        name="iPhone 16e 128GB",
        series="iPhone 16e Series",
        model_name="iPhone 16e",
        storage="128GB",
        ram="8GB",
        color="Black",
        price_inr=59900,
        rating=4.5,
        ai_score=87,
        display='6.1" Super Retina XDR OLED, 60Hz',
        chip="Apple A18",
        camera="48MP main",
        battery="3561mAh, 20W wired",
        affiliate_url="https://link.amazon/B071Vacq5",
        image_url="/images/products/iphone16pro-1.svg",
        pros=["Affordable iPhone entry", "Good daily performance", "Compact design"],
        cons=["Single rear camera", "No ProMotion", "Charging is modest"],
        best_for=["first-time iPhone buyers", "budget iOS users", "compact phone lovers"],
        not_for=["camera enthusiasts", "power gamers"],
        tags=["iphone", "apple", "5g", "ios", "budget", "compact", "smartphone"],
    ),
]


EXISTING_URL_ONLY: dict[str, str] = {
    "apple-iphone-16-128gb": "https://link.amazon/B06GgJfv6",
    "apple-iphone-16-plus-256gb": "https://link.amazon/B04u0A9g6",
}


def ensure_apple_brand(session) -> Brand:
    existing = session.scalars(select(Brand).where(Brand.name == "Apple")).first()
    if existing:
        return existing

    brand = Brand(name="Apple", slug="apple")
    session.add(brand)
    session.flush()
    return brand


def resolve_phone_category(session) -> Category:
    category = session.scalars(select(Category).where(Category.slug == "smartphones")).first()
    if category:
        return category

    category = session.scalars(select(Category).where(Category.slug == "phone")).first()
    if category:
        return category

    category = Category(name="Smartphones", slug="smartphones")
    session.add(category)
    session.flush()
    return category


def _insert_product(session, product: VerifiedPhone, brand: Brand, category: Category) -> None:
    db_product = Product(
        slug=product.slug,
        name=product.name,
        description=(
            f"{product.model_name} is a {product.chip}-powered smartphone in the {product.series} lineup. "
            f"It features a {product.display} display with {product.storage} storage and {product.ram} RAM. "
            f"The camera system packs {product.camera}. Battery: {product.battery}."
        ),
        availability="In Stock",
        category_id=category.id,
        brand_id=brand.id,
        price_value=inr(product.price_inr),
        currency="INR",
        rating=Decimal(str(product.rating)),
        ai_score=product.ai_score,
        ai_summary=(
            f"{product.model_name} scores {product.ai_score}/100. Powered by {product.chip}, "
            f"it excels in {product.best_for[0]}."
        ),
        review_summary=(
            f"Users love the {product.pros[0].lower()}. "
            f"Most common concern: {product.cons[0].lower()}."
        ),
        series=product.series,
        model_name=product.model_name,
        variant=f"{product.storage} / {product.ram} RAM / {product.color}",
        storage=product.storage,
        ram=product.ram,
        color=product.color,
        amazon_affiliate_url=product.affiliate_url,
    )
    session.add(db_product)
    session.flush()

    session.add(ProductImage(product_id=db_product.id, url=product.image_url, position=1))

    specs = [
        ("Display", product.display),
        ("Chip", product.chip),
        ("Camera", product.camera),
        ("Battery", product.battery),
        ("Storage", product.storage),
        ("RAM", product.ram),
        ("Color", product.color),
        ("OS", "iOS 18"),
        ("Network", "5G"),
    ]
    for position, (label, value) in enumerate(specs, start=1):
        session.add(ProductSpecification(product_id=db_product.id, label=label, value=value, position=position))

    features = [
        product.display,
        product.chip,
        product.camera,
        product.battery,
        f"{product.storage} internal storage",
        f"{product.ram} RAM",
    ]
    for position, value in enumerate(features, start=1):
        session.add(ProductFeature(product_id=db_product.id, value=value, position=position))

    for position, value in enumerate(product.pros[:3], start=1):
        session.add(ProductPro(product_id=db_product.id, value=value, position=position))
    for position, value in enumerate(product.cons[:3], start=1):
        session.add(ProductCon(product_id=db_product.id, value=value, position=position))
    for position, value in enumerate(product.best_for[:3], start=1):
        session.add(ProductBestFor(product_id=db_product.id, value=value, position=position))
    for position, value in enumerate(product.not_for[:2], start=1):
        session.add(ProductNotRecommendedFor(product_id=db_product.id, value=value, position=position))

    tag_set = {"phone", "smartphone", "mobile", "5g", "apple", *product.tags, slugify(product.model_name)}
    for value in tag_set:
        session.add(ProductTag(product_id=db_product.id, value=value))

    for label, mult in [("Jan", 1.06), ("Feb", 1.04), ("Mar", 1.02), ("Apr", 1.01), ("May", 1.0), ("Now", 1.0)]:
        session.add(PriceHistory(product_id=db_product.id, label=label, price=inr(round(product.price_inr * mult / 100) * 100)))

    review_data = [
        ("Excellent daily driver", "Great purchase, exactly as described.", 4.5),
        ("Best phone I've owned", "Camera quality is impressive for the price.", 5.0),
        ("Worth every rupee", "Battery lasts a full day easily.", 4.5),
        ("Good with minor trade-offs", f"{product.cons[0]} is a real concern.", 3.5),
        ("Highly recommended", "Would definitely recommend to a friend.", 4.5),
    ]
    for idx, (title, comment, rating) in enumerate(review_data, start=1):
        session.add(
            Review(
                product_id=db_product.id,
                author=["Arjun S.", "Priya K.", "Rahul M.", "Sneha T.", "Vikram P."][idx - 1],
                title=title,
                rating=Decimal(str(rating)),
                comment=comment,
                date=["2026-03-15", "2026-04-20", "2026-05-10", "2026-06-05", "2026-07-12"][idx - 1],
            )
        )


def run() -> None:
    session = SessionLocal()
    try:
        brand = ensure_apple_brand(session)
        category = resolve_phone_category(session)

        created = 0
        updated = 0

        for slug, url in EXISTING_URL_ONLY.items():
            row = session.scalars(select(Product).where(Product.slug == slug)).first()
            if row and row.amazon_affiliate_url != url:
                row.amazon_affiliate_url = url
                updated += 1

        for product in VERIFIED_NEW_PHONES:
            row = session.scalars(select(Product).where(Product.slug == product.slug)).first()
            if row:
                if row.amazon_affiliate_url != product.affiliate_url:
                    row.amazon_affiliate_url = product.affiliate_url
                    updated += 1
                continue

            _insert_product(session, product, brand, category)
            created += 1

        session.commit()
        print(f"Verified Apple iPhones sync complete. Created: {created} | Updated URLs: {updated}", flush=True)
    finally:
        session.close()


if __name__ == "__main__":
    run()
