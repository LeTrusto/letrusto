import random
import re
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

from faker import Faker

from app.db.session import SessionLocal
from app.models.entities import (
    Brand,
    Category,
    PriceHistory,
    Product,
    ProductBestFor,
    ProductBuyLink,
    ProductCon,
    ProductFeature,
    ProductImage,
    ProductNotRecommendedFor,
    ProductPro,
    ProductSimilarity,
    ProductSpecification,
    ProductTag,
    Review,
)

fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)


@dataclass
class CategorySeed:
    slug: str
    name: str
    brands: list[str]
    nouns: list[str]
    features: list[str]
    specs: list[tuple[str, str]]
    pros: list[str]
    cons: list[str]
    best_for: list[str]
    not_recommended_for: list[str]
    tags: list[str]
    price_range: tuple[int, int]
    rating_range: tuple[float, float]
    ai_range: tuple[int, int]
    image_fallbacks: list[str]
    amazon_asin: str | None = None
    amazon_affiliate_url: str | None = None
    flipkart_affiliate_url: str | None = None


CATEGORY_SEEDS: list[CategorySeed] = [
    CategorySeed(
        slug="phone",
        name="Phone",
        brands=["Apple", "Samsung", "OnePlus", "Nothing", "Motorola", "Xiaomi", "Google"],
        nouns=["Ultra", "Pro", "Plus", "Air", "Neo", "Prime", "Max"],
        features=["AMOLED display", "fast charging", "optical image stabilization", "AI camera tools", "all-day battery"],
        specs=[("Display", "6.6-inch AMOLED 120Hz"), ("Chip", "Snapdragon 8-series"), ("Storage", "256GB"), ("Battery", "5000mAh"), ("Camera", "50MP primary sensor")],
        pros=["Strong performance for daily apps", "Reliable camera in daylight", "Good battery endurance"],
        cons=["Low-light photos need tuning", "Premium variants are expensive", "No charger in some variants"],
        best_for=["mobile photography", "social media creators", "power users"],
        not_recommended_for=["ultra-tight budgets", "small-phone lovers", "stock-android purists"],
        tags=["phone", "android", "camera", "flagship", "battery"],
        price_range=(18000, 125000),
        rating_range=(4.1, 4.9),
        ai_range=(82, 97),
        image_fallbacks=[
            "/images/products/iphone16pro-1.svg",
            "/images/products/galaxy-s25-1.png",
            "/images/products/nothing-phone-2a-1.jpg",
            "/images/products/oneplus-nord-4-1.jpg",
        ],
    ),
    CategorySeed(
        slug="laptop",
        name="Laptop",
        brands=["Apple", "ASUS", "Lenovo", "Dell", "HP", "Acer", "MSI"],
        nouns=["Book", "Air", "Edge", "Pro", "Carbon", "Studio", "Flex"],
        features=["high-efficiency chip", "lightweight chassis", "color-accurate display", "long battery", "fast SSD"],
        specs=[("Display", "14-inch 2.8K panel"), ("Chip", "Core Ultra class processor"), ("Memory", "16GB"), ("Storage", "1TB SSD"), ("Battery", "70Wh")],
        pros=["Strong productivity performance", "Good keyboard and trackpad", "Portable for travel"],
        cons=["Upgrades are limited", "Premium tiers are expensive", "Fan noise under sustained load"],
        best_for=["coding workloads", "office productivity", "students"],
        not_recommended_for=["heavy AAA gaming", "budget-only buyers", "desktop replacement needs"],
        tags=["laptop", "developer", "productivity", "office", "portable"],
        price_range=(45000, 210000),
        rating_range=(4.1, 4.9),
        ai_range=(80, 98),
        image_fallbacks=[
            "/images/products/macbook-air-m4.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/MacBook_Air_M2.png/1280px-MacBook_Air_M2.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/ThinkPad_X1_Carbon_Gen_6.jpg/1280px-ThinkPad_X1_Carbon_Gen_6.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Dell_XPS_13_7390_2-in-1.jpg/1280px-Dell_XPS_13_7390_2-in-1.jpg",
        ],
    ),
    CategorySeed(
        slug="headphones",
        name="Headphones",
        brands=["Sony", "Bose", "Apple", "Sennheiser", "JBL", "Anker", "Beats"],
        nouns=["Tune", "Quiet", "Studio", "Pulse", "Momentum", "Wave", "ANC"],
        features=["active noise cancellation", "spatial audio", "clear call microphones", "multi-device pairing", "long battery"],
        specs=[("Driver", "40mm dynamic"), ("Battery", "30 hours"), ("Connectivity", "Bluetooth 5.3"), ("Charging", "USB-C"), ("Weight", "260g")],
        pros=["Comfortable fit for long sessions", "Good ANC performance", "Clean audio tuning"],
        cons=["Premium pricing", "Touch controls need practice", "Case can be bulky"],
        best_for=["office focus", "travel", "daily music listening"],
        not_recommended_for=["audiophile wired setups", "ultra-low budgets", "tiny carrying cases"],
        tags=["headphones", "music", "anc", "travel", "wireless"],
        price_range=(6000, 65000),
        rating_range=(4.0, 4.9),
        ai_range=(78, 95),
        image_fallbacks=[
            "/images/products/bose-qc-ultra-1.jpg",
            "/images/products/sony-wh1000xm6.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/AirPods_Max.png/1280px-AirPods_Max.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Headphones_1.jpg/1280px-Headphones_1.jpg",
        ],
    ),
    CategorySeed(
        slug="smartwatch",
        name="Smart Watch",
        brands=["Apple", "Samsung", "Garmin", "OnePlus", "Amazfit", "Fitbit"],
        nouns=["Watch", "Active", "Venu", "Balance", "Sport", "Trail", "Pulse"],
        features=["health tracking", "bright OLED screen", "sleep insights", "GPS tracking", "water resistance"],
        specs=[("Display", "1.4-inch OLED"), ("Battery", "Up to 5 days"), ("Sensors", "HR, SpO2, sleep"), ("GPS", "Dual-band GPS"), ("Water Resistance", "5 ATM")],
        pros=["Accurate fitness metrics", "Comfortable all-day wear", "Solid notification handling"],
        cons=["App ecosystem varies by brand", "LTE models cost extra", "Some metrics need calibration"],
        best_for=["fitness tracking", "health monitoring", "daily notifications"],
        not_recommended_for=["week-long battery demands", "full-phone replacement", "budget-only buyers"],
        tags=["smartwatch", "fitness", "health", "wearable", "gps"],
        price_range=(7000, 60000),
        rating_range=(4.0, 4.8),
        ai_range=(76, 94),
        image_fallbacks=[
            "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Samsung_Galaxy_Watch.jpg/1280px-Samsung_Galaxy_Watch.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Apple_Watch.jpg/1280px-Apple_Watch.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Garmin_watch.jpg/1280px-Garmin_watch.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Smart_watch.jpg/1280px-Smart_watch.jpg",
        ],
    ),
    CategorySeed(
        slug="television",
        name="Television",
        brands=["LG", "Samsung", "Sony", "TCL", "Hisense", "Panasonic"],
        nouns=["Vision", "Cinema", "Neo", "Bravia", "QLED", "OLED", "Ultra"],
        features=["4K resolution", "HDR support", "high refresh gaming mode", "smart TV apps", "low reflection panel"],
        specs=[("Panel", "4K QLED/OLED"), ("Refresh Rate", "120Hz"), ("HDMI", "4 ports"), ("Audio", "40W") , ("OS", "Google TV / Tizen")],
        pros=["Strong picture quality", "Good gaming responsiveness", "Modern smart features"],
        cons=["Top-end models are costly", "OS updates vary by brand", "Audio may need soundbar"],
        best_for=["movie nights", "console gaming", "family living rooms"],
        not_recommended_for=["very small spaces", "entry-level budgets", "legacy input needs"],
        tags=["television", "tv", "4k", "gaming", "streaming"],
        price_range=(25000, 240000),
        rating_range=(4.1, 4.9),
        ai_range=(79, 96),
        image_fallbacks=[
            "/images/products/sony-bravia-7-55-1.jpg",
            "/images/products/tcl-c755-55-1.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Samsung_LED_TV.jpg/1280px-Samsung_LED_TV.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Flat_screen_TV.jpg/1280px-Flat_screen_TV.jpg",
        ],
    ),
    CategorySeed(
        slug="refrigerator",
        name="Refrigerator",
        brands=["Samsung", "LG", "Whirlpool", "Haier", "Godrej", "Bosch"],
        nouns=["Cool", "Fresh", "Frost", "Insta", "Bespoke", "Twin", "Max"],
        features=["frost-free cooling", "inverter compressor", "convertible storage", "odor control", "spill-proof shelves"],
        specs=[("Capacity", "350L"), ("Cooling", "Frost Free"), ("Compressor", "Inverter"), ("Energy Rating", "3 Star"), ("Type", "Double Door")],
        pros=["Efficient cooling consistency", "Useful internal organization", "Low operating noise"],
        cons=["Premium finishes increase price", "Large units need more space", "Energy rating varies"],
        best_for=["family kitchens", "weekly grocery storage", "modern interiors"],
        not_recommended_for=["studio apartments", "very low budgets", "single-person minimal needs"],
        tags=["refrigerator", "fridge", "kitchen", "appliance", "family"],
        price_range=(18000, 180000),
        rating_range=(4.0, 4.8),
        ai_range=(74, 93),
        image_fallbacks=[
            "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Open_refrigerator_with_food_at_night.jpg/1280px-Open_refrigerator_with_food_at_night.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Refrigerator.jpg/1280px-Refrigerator.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Fridge_open.jpg/1280px-Fridge_open.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Frigorifero_Double_Door.jpg/1280px-Frigorifero_Double_Door.jpg",
        ],
    ),
    CategorySeed(
        slug="washing-machine",
        name="Washing Machine",
        brands=["LG", "Samsung", "IFB", "Bosch", "Whirlpool", "Panasonic"],
        nouns=["Wash", "Eco", "Steam", "Smart", "Turbo", "Direct", "Clean"],
        features=["multiple wash programs", "inverter motor", "steam hygiene", "fabric care mode", "low vibration"],
        specs=[("Type", "Front Load"), ("Capacity", "8kg"), ("Motor", "Inverter"), ("Programs", "12+"), ("Spin", "1200 RPM")],
        pros=["Effective stain removal", "Good fabric protection", "Reasonable power usage"],
        cons=["Longer cycle times", "Front-loads cost more", "Service quality is location-dependent"],
        best_for=["family laundry", "fabric care", "energy-conscious homes"],
        not_recommended_for=["quick-only wash needs", "minimal install space", "entry-level budgets"],
        tags=["washing-machine", "laundry", "appliance", "family", "home"],
        price_range=(14000, 90000),
        rating_range=(4.0, 4.8),
        ai_range=(72, 92),
        image_fallbacks=[
            "/images/products/ifb-senator-mxn-8012-1.jpg",
            "/images/products/whirlpool-stainwash-pro-9kg-1.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/e/ec/LG_%EB%93%9C%EB%9F%BC%EC%84%B8%ED%83%81%EA%B8%B0%EC%99%80_%EC%8B%9D%EA%B8%B0%EC%84%B8%EC%B2%99%EA%B8%B0%2C_%EC%98%81%EA%B5%AD%EC%84%9C_%EB%AC%BC%EC%82%AC%EC%9A%A9_%ED%9A%A8%EC%9C%A8_%EC%B5%9C%EC%9A%B0%EC%88%98_%EC%A0%9C%ED%92%88_%EC%88%98%EC%83%81.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Washing_machine.jpg/1280px-Washing_machine.jpg",
        ],
    ),
    CategorySeed(
        slug="gaming",
        name="Gaming",
        brands=["Sony", "Microsoft", "Nintendo", "ASUS", "Lenovo", "Valve"],
        nouns=["Console", "Slim", "Deck", "Go", "X", "Elite", "Core"],
        features=["high frame-rate gaming", "fast SSD load times", "strong game library", "ray tracing support", "portable mode"],
        specs=[("Platform", "Console/Handheld"), ("Storage", "1TB"), ("Output", "Up to 4K 120Hz"), ("Connectivity", "Wi-Fi 6"), ("Controller", "Included")],
        pros=["Great game library", "Smooth performance", "Easy setup for living-room gaming"],
        cons=["Subscription costs add up", "Accessory ecosystem can be expensive", "Large updates consume storage"],
        best_for=["console gaming", "family multiplayer", "portable play"],
        not_recommended_for=["keyboard-mouse competitive players", "ultra-low budgets", "office-only usage"],
        tags=["gaming", "console", "portable", "4k", "ssd"],
        price_range=(18000, 90000),
        rating_range=(4.1, 4.9),
        ai_range=(78, 96),
        image_fallbacks=[
            "/images/products/nintendo-switch-oled-1.png",
            "/images/products/lenovo-legion-go-1.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Black_and_white_Playstation_5_base_edition_with_controller.png/1280px-Black_and_white_Playstation_5_base_edition_with_controller.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Xbox_series_X_and_series_S_with_controller.jpg/1280px-Xbox_series_X_and_series_S_with_controller.jpg",
        ],
    ),
    CategorySeed(
        slug="tablet",
        name="Tablet",
        brands=["Apple", "Samsung", "OnePlus", "Xiaomi", "Lenovo", "Huawei"],
        nouns=["Pad", "Air", "Tab", "Pro", "Lite", "Max", "Note"],
        features=["large high-resolution display", "stylus support", "good battery life", "lightweight design", "multitasking mode"],
        specs=[("Display", "11-inch 2.8K"), ("Chip", "Flagship class SoC"), ("Storage", "256GB"), ("Battery", "9000mAh"), ("Accessories", "Keyboard + Stylus")],
        pros=["Great for media and notes", "Portable for travel", "Good app ecosystem"],
        cons=["Desktop replacement is limited", "Accessories can cost extra", "Premium models are pricey"],
        best_for=["students", "media consumption", "portable productivity"],
        not_recommended_for=["heavy desktop workflows", "budget-only buyers", "small-screen preferences"],
        tags=["tablet", "student", "media", "stylus", "productivity"],
        price_range=(12000, 110000),
        rating_range=(4.0, 4.8),
        ai_range=(75, 94),
        image_fallbacks=[
            "/images/products/ipad-air-m2-1.jpg",
            "/images/products/samsung-galaxy-tab-s10-1.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/IPad_Mini_6_-_1.jpg/1280px-IPad_Mini_6_-_1.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Tablet_computer.jpg/1280px-Tablet_computer.jpg",
        ],
    ),
    CategorySeed(
        slug="camera",
        name="Camera",
        brands=["Sony", "Canon", "Nikon", "Fujifilm", "Panasonic", "GoPro"],
        nouns=["Alpha", "EOS", "Z", "X", "Hero", "Lumix", "Mark"],
        features=["fast autofocus", "high dynamic range", "4K video", "in-body stabilization", "lens ecosystem"],
        specs=[("Sensor", "Full-frame / APS-C"), ("Video", "4K 60fps"), ("Stabilization", "IBIS"), ("Autofocus", "Subject tracking"), ("Storage", "Dual card slots")],
        pros=["Excellent image quality", "Reliable autofocus", "Strong creator workflow support"],
        cons=["Body and lenses are expensive", "Battery life varies", "Beginners face a learning curve"],
        best_for=["hybrid creators", "travel content", "professional photography"],
        not_recommended_for=["casual phone-only users", "tight budgets", "zero-edit workflows"],
        tags=["camera", "mirrorless", "creator", "video", "photography"],
        price_range=(25000, 350000),
        rating_range=(4.1, 4.9),
        ai_range=(80, 97),
        image_fallbacks=[
            "/images/products/sony-a7-iv-1.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Canon_EOS_R6.jpg/1280px-Canon_EOS_R6.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Nikon_Z6_camera.jpg/1280px-Nikon_Z6_camera.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Mirrorless_camera.jpg/1280px-Mirrorless_camera.jpg",
        ],
    ),
]


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"(^-|-$)", "", value)
    return value


def pick_price(min_price: int, max_price: int) -> Decimal:
    raw = random.randint(min_price // 1000, max_price // 1000) * 1000
    return Decimal(raw)


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def build_buy_links(brand: str, name: str) -> list[tuple[str, str]]:
    query = f"{brand} {name}".replace(" ", "+")
    return [
        ("Flipkart", f"https://www.flipkart.com/search?q={query}"),
        ("Croma", f"https://www.croma.com/searchB?q={query}%3Arelevance"),
        ("Reliance Digital", f"https://www.reliancedigital.in/search?q={query}"),
    ]


def reset_tables(session):
    tables = [
        ProductSimilarity,
        ProductBuyLink,
        Review,
        PriceHistory,
        ProductTag,
        ProductNotRecommendedFor,
        ProductBestFor,
        ProductCon,
        ProductPro,
        ProductFeature,
        ProductSpecification,
        ProductImage,
        Product,
        Brand,
        Category,
    ]
    for model in tables:
        session.query(model).delete()
    session.commit()


def seed() -> None:
    session = SessionLocal()
    try:
        reset_tables(session)

        category_records: dict[str, Category] = {}
        brand_records: dict[str, Brand] = {}

        for seed in CATEGORY_SEEDS:
            category = Category(name=seed.name, slug=seed.slug)
            session.add(category)
            category_records[seed.slug] = category

        all_brands = sorted({brand for seed in CATEGORY_SEEDS for brand in seed.brands})
        for brand_name in all_brands:
            brand = Brand(name=brand_name, slug=slugify(brand_name))
            session.add(brand)
            brand_records[brand_name] = brand

        session.flush()

        products_by_category: dict[str, list[Product]] = defaultdict(list)

        for seed in CATEGORY_SEEDS:
            for idx in range(1, 31):
                brand_name = random.choice(seed.brands)
                brand = brand_records[brand_name]
                model_token = random.choice(seed.nouns)
                name = f"{brand_name} {model_token} {idx}"
                slug = slugify(name)

                price = pick_price(*seed.price_range)
                rating = Decimal(str(round(clamp(random.uniform(*seed.rating_range), 3.8, 5.0), 1)))
                ai_score = int(clamp(random.randint(*seed.ai_range), 70, 99))

                feature_a = random.choice(seed.features)
                feature_b = random.choice([item for item in seed.features if item != feature_a])

                product = Product(
                    slug=slug,
                    name=name,
                    description=(
                        f"{name} is built for {random.choice(seed.best_for)} with {feature_a} and {feature_b} "
                        f"as core strengths."
                    ),
                    availability=random.choice(["In Stock", "Limited Stock", "Pre-order"]),
                    category_id=category_records[seed.slug].id,
                    brand_id=brand.id,
                    price_value=price,
                    currency="INR",
                    rating=rating,
                    ai_score=ai_score,
                    ai_summary=(
                        f"{name} scores {ai_score}/100 for balancing {feature_a} with {feature_b}, "
                        f"making it a strong fit for {seed.best_for[0]}."
                    ),
                    review_summary=(
                        f"Buyers highlight {seed.pros[0].lower()} and {seed.pros[1].lower()}, "
                        f"while noting {seed.cons[0].lower()}."
                    ),
                )
                session.add(product)
                session.flush()

                for position, image_url in enumerate(seed.image_fallbacks, start=1):
                    session.add(ProductImage(product_id=product.id, url=image_url, position=position))

                varied_specs = [
                    (label, value.replace("8kg", f"{random.choice([7, 8, 9, 10])}kg").replace("350L", f"{random.choice([280, 320, 360, 420])}L"))
                    for label, value in seed.specs
                ]
                for position, (label, value) in enumerate(varied_specs, start=1):
                    session.add(
                        ProductSpecification(
                            product_id=product.id,
                            label=label,
                            value=value,
                            position=position,
                        )
                    )

                for position, value in enumerate(random.sample(seed.features, k=min(4, len(seed.features))), start=1):
                    session.add(ProductFeature(product_id=product.id, value=value, position=position))

                for position, value in enumerate(seed.pros[:3], start=1):
                    session.add(ProductPro(product_id=product.id, value=value, position=position))

                for position, value in enumerate(seed.cons[:2], start=1):
                    session.add(ProductCon(product_id=product.id, value=value, position=position))

                for position, value in enumerate(seed.best_for[:2], start=1):
                    session.add(ProductBestFor(product_id=product.id, value=value, position=position))

                for position, value in enumerate(seed.not_recommended_for[:2], start=1):
                    session.add(ProductNotRecommendedFor(product_id=product.id, value=value, position=position))

                for tag in {seed.slug, brand.slug, *seed.tags}:
                    session.add(ProductTag(product_id=product.id, value=tag))

                base = int(price)
                for label, multiplier in [("Jan", 1.08), ("Feb", 1.05), ("Mar", 1.03), ("Apr", 1.02), ("May", 0.99), ("Now", 1.0)]:
                    session.add(
                        PriceHistory(
                            product_id=product.id,
                            label=label,
                            price=Decimal(round((base * multiplier) / 100) * 100),
                        )
                    )

                for r_idx in range(1, 6):
                    review_rating = Decimal(str(round(clamp(float(rating) - random.uniform(0, 0.7), 3.8, 5.0), 1)))
                    session.add(
                        Review(
                            product_id=product.id,
                            author=fake.first_name() + " " + fake.last_name()[0] + ".",
                            title=random.choice([
                                "Worth the shortlist",
                                "Great value for this segment",
                                "Strong daily performer",
                                "Good with minor tradeoffs",
                                "Would recommend",
                            ]),
                            rating=review_rating,
                            comment=f"Using this for {random.choice(seed.best_for)}. {random.choice(seed.pros)}.",
                            date=f"2026-0{random.randint(4, 7)}-{random.randint(10, 28)}",
                        )
                    )

                for label, href in build_buy_links(brand_name, name):
                    session.add(ProductBuyLink(product_id=product.id, label=label, href=href))

                products_by_category[seed.slug].append(product)

        session.flush()

        # Similarity links by category and score proximity.
        for seed in CATEGORY_SEEDS:
            category_products = products_by_category[seed.slug]
            for product in category_products:
                candidates = [item for item in category_products if item.id != product.id]
                candidates = sorted(
                    candidates,
                    key=lambda item: abs(item.ai_score - product.ai_score) + abs(float(item.rating) - float(product.rating)) * 5,
                )
                for similar in candidates[:8]:
                    score = 100 - int(abs(similar.ai_score - product.ai_score))
                    session.add(
                        ProductSimilarity(
                            product_id=product.id,
                            similar_product_id=similar.id,
                            score=max(60, score),
                        )
                    )

        session.commit()
        total_products = session.query(Product).count()
        print(f"Seed completed: {total_products} products created.")
    finally:
        session.close()


if __name__ == "__main__":
    seed()
