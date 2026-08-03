"""
Phase 6.2 — Smartphone Catalog Seed
Populates the 'smartphones' subcategory with realistic models from 14 brands.
Run from the backend/ directory:
    python -m scripts.seed_smartphones
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
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


# ── Helpers ──────────────────────────────────────────────────────────────────

def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"(^-|-$)", "", value)


def inr(amount: int) -> Decimal:
    return Decimal(str(amount))


# ── Phone model definition ────────────────────────────────────────────────────

@dataclass
class PhoneModel:
    brand: str
    series: str
    model_name: str
    ram: str
    storage_variants: list[tuple[str, int]]  # (storage_label, price_INR)
    color: str
    rating: float
    ai_score: int
    display: str
    chip: str
    camera: str
    battery: str
    pros: list[str]
    cons: list[str]
    best_for: list[str]
    not_for: list[str]
    tags: list[str]
    image_url: str
    availability: str = "In Stock"
    extra_specs: list[tuple[str, str]] = field(default_factory=list)


# ── Phone catalog ─────────────────────────────────────────────────────────────

PHONES: list[PhoneModel] = [

    # ── Apple ────────────────────────────────────────────────────────────────
    PhoneModel(
        brand="Apple", series="iPhone 16 Series", model_name="iPhone 16 Pro Max",
        ram="8GB", color="Black Titanium",
        storage_variants=[
            ("256GB", 134900), ("512GB", 154900), ("1TB", 174900),
        ],
        rating=4.9, ai_score=98,
        display='6.9" Super Retina XDR OLED, 1-120Hz ProMotion',
        chip="Apple A18 Pro",
        camera="48MP main + 48MP ultrawide + 12MP 5× telephoto",
        battery="5000mAh, 30W wired, 25W MagSafe",
        pros=["Best-in-class iPhone camera system", "Incredible A18 Pro performance", "Premium titanium build", "ProRes video recording", "Long software support"],
        cons=["Very expensive", "No charger in box", "Heavy at 227g", "USB-C still limited to USB 3 speed on base"],
        best_for=["professional photography", "videography", "power users", "iOS ecosystem"],
        not_for=["budget buyers", "small-phone lovers", "Android users"],
        tags=["iphone", "apple", "flagship", "5g", "camera", "ios", "titanium", "promax"],
        image_url="/images/products/iphone16pro-1.svg",
        extra_specs=[("Network", "5G"), ("OS", "iOS 18"), ("Charging", "30W wired + 25W MagSafe"), ("Colors", "Black/White/Natural/Desert Titanium")],
    ),
    PhoneModel(
        brand="Apple", series="iPhone 16 Series", model_name="iPhone 16 Pro",
        ram="8GB", color="Natural Titanium",
        storage_variants=[
            ("128GB", 119900), ("256GB", 129900), ("512GB", 149900), ("1TB", 169900),
        ],
        rating=4.9, ai_score=97,
        display='6.3" Super Retina XDR OLED, 1-120Hz ProMotion',
        chip="Apple A18 Pro",
        camera="48MP main + 48MP ultrawide + 12MP 5× telephoto",
        battery="4490mAh, 30W wired",
        pros=["A18 Pro chip with AI features", "Compact premium flagship", "Excellent camera versatility", "Long iOS update support"],
        cons=["Starts at high price", "Heavy titanium chassis", "No charger included"],
        best_for=["compact flagship seekers", "Apple ecosystem users", "mobile photographers"],
        not_for=["budget shoppers", "Android fans", "one-hand use purists"],
        tags=["iphone", "apple", "flagship", "5g", "pro", "ios", "camera"],
        image_url="/images/products/iphone16pro-1.svg",
        extra_specs=[("Network", "5G"), ("OS", "iOS 18"), ("Charging", "30W wired + 25W MagSafe")],
    ),
    PhoneModel(
        brand="Apple", series="iPhone 16 Series", model_name="iPhone 16 Plus",
        ram="8GB", color="Teal",
        storage_variants=[
            ("128GB", 89900), ("256GB", 99900), ("512GB", 119900),
        ],
        rating=4.7, ai_score=93,
        display='6.7" Super Retina XDR OLED, 60Hz',
        chip="Apple A18",
        camera="48MP main + 12MP ultrawide",
        battery="4674mAh, 25W wired",
        pros=["Large screen with great brightness", "A18 chip with Apple Intelligence", "Long battery life", "Good camera system"],
        cons=["60Hz display at this price", "No telephoto lens", "Larger and heavier"],
        best_for=["large-screen lovers", "media consumption", "iOS users on budget flagship"],
        not_for=["compact phone users", "Pro camera needs", "gaming enthusiasts"],
        tags=["iphone", "apple", "5g", "ios", "plus", "battery"],
        image_url="/images/products/iphone16pro-1.svg",
        extra_specs=[("Network", "5G"), ("OS", "iOS 18"), ("Charging", "25W wired + MagSafe")],
    ),
    PhoneModel(
        brand="Apple", series="iPhone 16 Series", model_name="iPhone 16",
        ram="8GB", color="Ultramarine",
        storage_variants=[
            ("128GB", 79900), ("256GB", 89900), ("512GB", 109900),
        ],
        rating=4.7, ai_score=92,
        display='6.1" Super Retina XDR OLED, 60Hz',
        chip="Apple A18",
        camera="48MP main + 12MP ultrawide",
        battery="3561mAh, 25W wired",
        pros=["Compact flagship form factor", "A18 chip performance", "Apple Intelligence on device", "Bright outdoor display"],
        cons=["60Hz refresh rate", "Smaller battery", "No telephoto"],
        best_for=["iOS beginners", "compact design lovers", "everyday use"],
        not_for=["heavy gaming", "battery-intensive users", "Android users"],
        tags=["iphone", "apple", "5g", "ios", "compact", "ai"],
        image_url="/images/products/iphone16pro-1.svg",
        extra_specs=[("Network", "5G"), ("OS", "iOS 18"), ("Charging", "25W wired + MagSafe")],
    ),
    PhoneModel(
        brand="Apple", series="iPhone 15 Series", model_name="iPhone 15 Pro Max",
        ram="8GB", color="Natural Titanium",
        storage_variants=[
            ("256GB", 124900), ("512GB", 144900), ("1TB", 164900),
        ],
        rating=4.8, ai_score=96,
        display='6.7" Super Retina XDR OLED, 1-120Hz ProMotion',
        chip="Apple A17 Pro",
        camera="48MP main + 12MP ultrawide + 12MP 5× telephoto",
        battery="4422mAh, 27W wired",
        pros=["A17 Pro chip still very capable", "Titanium build quality", "Excellent 5× telephoto", "USB 3.2 speed via USB-C"],
        cons=["One generation old", "Expensive for 2024 chip", "No Apple Intelligence features"],
        best_for=["previous-gen flagship value", "photography", "iOS power users"],
        not_for=["buyers wanting Apple Intelligence", "cutting-edge chip seekers"],
        tags=["iphone", "apple", "flagship", "5g", "titanium", "telephoto", "ios"],
        image_url="/images/products/iphone16pro-1.svg",
        extra_specs=[("Network", "5G"), ("OS", "iOS 17 → 18"), ("Charging", "27W wired + MagSafe")],
    ),
    PhoneModel(
        brand="Apple", series="iPhone 15 Series", model_name="iPhone 15 Pro",
        ram="8GB", color="Blue Titanium",
        storage_variants=[
            ("128GB", 99900), ("256GB", 109900), ("512GB", 129900),
        ],
        rating=4.8, ai_score=95,
        display='6.1" Super Retina XDR OLED, 1-120Hz ProMotion',
        chip="Apple A17 Pro",
        camera="48MP main + 12MP ultrawide + 12MP 3× telephoto",
        battery="3274mAh, 27W wired",
        pros=["Powerful A17 Pro performance", "Compact Pro form factor", "Great HDR display", "Durable titanium frame"],
        cons=["Small battery", "Previous-gen chip era", "No Apple Intelligence"],
        best_for=["compact flagship lovers", "professional workflows", "photography"],
        not_for=["battery life priority", "AI feature seekers"],
        tags=["iphone", "apple", "pro", "5g", "compact", "ios"],
        image_url="/images/products/iphone16pro-1.svg",
        extra_specs=[("Network", "5G"), ("OS", "iOS 17 → 18")],
    ),
    PhoneModel(
        brand="Apple", series="iPhone 15 Series", model_name="iPhone 15",
        ram="6GB", color="Pink",
        storage_variants=[
            ("128GB", 64900), ("256GB", 74900),
        ],
        rating=4.6, ai_score=89,
        display='6.1" Super Retina XDR OLED, 60Hz',
        chip="Apple A16 Bionic",
        camera="48MP main + 12MP ultrawide",
        battery="3349mAh, 23W wired",
        pros=["USB-C charging", "48MP camera upgrade", "Dynamic Island", "Solid everyday performance"],
        cons=["60Hz display", "No telephoto", "A16 is aging"],
        best_for=["mainstream iOS users", "everyday photography", "upgrading from older iPhones"],
        not_for=["Pro camera needs", "gaming", "heavy multitasking"],
        tags=["iphone", "apple", "ios", "5g", "mainstreamflagship"],
        image_url="/images/products/iphone16pro-1.svg",
        extra_specs=[("Network", "5G"), ("OS", "iOS 17 → 18")],
    ),
    PhoneModel(
        brand="Apple", series="iPhone SE Series", model_name="iPhone SE (3rd Gen)",
        ram="4GB", color="Midnight",
        storage_variants=[
            ("64GB", 49900), ("128GB", 54900), ("256GB", 64900),
        ],
        rating=4.3, ai_score=80,
        display='4.7" Retina HD LCD, 60Hz',
        chip="Apple A15 Bionic",
        camera="12MP main (single lens)",
        battery="2018mAh, 20W wired",
        pros=["Compact and lightweight", "Strong A15 chip", "5G connectivity", "Affordable iOS entry"],
        cons=["Very small battery", "Old design with bezels", "Single camera only", "60Hz LCD display"],
        best_for=["compact phone lovers", "budget iOS buyers", "elderly users"],
        not_for=["photography", "gaming", "large-screen users", "media consumption"],
        tags=["iphone", "apple", "compact", "budget", "5g", "ios", "se"],
        image_url="/images/products/iphone16pro-1.svg",
        extra_specs=[("Network", "5G"), ("OS", "iOS 15 → 18")],
    ),

    # ── Samsung ──────────────────────────────────────────────────────────────
    PhoneModel(
        brand="Samsung", series="Galaxy S25 Series", model_name="Samsung Galaxy S25 Ultra",
        ram="12GB", color="Titanium Black",
        storage_variants=[
            ("256GB", 129999), ("512GB", 149999), ("1TB", 169999),
        ],
        rating=4.9, ai_score=98,
        display='6.9" Dynamic AMOLED 2X, 1-120Hz',
        chip="Snapdragon 8 Elite",
        camera="200MP main + 50MP ultrawide + 10MP 3× + 50MP 5× telephoto",
        battery="5000mAh, 45W wired + 15W wireless",
        pros=["Best Android camera system", "S Pen included", "Snapdragon 8 Elite peak performance", "Galaxy AI features", "Titanium frame build"],
        cons=["Very expensive", "Bulky and heavy", "S Pen less useful for some", "One UI bloatware"],
        best_for=["S Pen productivity", "professional photography", "Android power users", "business use"],
        not_for=["budget buyers", "compact phone seekers", "iOS users"],
        tags=["samsung", "galaxy", "s25", "ultra", "flagship", "5g", "spen", "android"],
        image_url="/images/products/galaxy-s25-1.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 15, One UI 7"), ("Charging", "45W wired + 15W wireless"), ("S Pen", "Included")],
    ),
    PhoneModel(
        brand="Samsung", series="Galaxy S25 Series", model_name="Samsung Galaxy S25+",
        ram="12GB", color="Icy Blue",
        storage_variants=[
            ("256GB", 99999), ("512GB", 119999),
        ],
        rating=4.8, ai_score=96,
        display='6.7" Dynamic AMOLED 2X, 1-120Hz',
        chip="Snapdragon 8 Elite",
        camera="50MP main + 12MP ultrawide + 10MP 3× telephoto",
        battery="4900mAh, 45W wired + 15W wireless",
        pros=["Large screen with smooth 120Hz", "Excellent Snapdragon 8 Elite chip", "Clean Galaxy AI features", "Good camera system"],
        cons=["Missing S Pen vs Ultra", "No 5× zoom", "Premium pricing"],
        best_for=["large-screen Android users", "productivity", "media consumption"],
        not_for=["compact phone lovers", "S Pen users", "budget buyers"],
        tags=["samsung", "galaxy", "s25", "plus", "flagship", "5g", "android"],
        image_url="/images/products/galaxy-s25-1.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 15, One UI 7"), ("Charging", "45W wired + 15W wireless")],
    ),
    PhoneModel(
        brand="Samsung", series="Galaxy S25 Series", model_name="Samsung Galaxy S25",
        ram="12GB", color="Navy",
        storage_variants=[
            ("128GB", 79999), ("256GB", 89999),
        ],
        rating=4.8, ai_score=95,
        display='6.2" Dynamic AMOLED 2X, 1-120Hz',
        chip="Snapdragon 8 Elite",
        camera="50MP main + 12MP ultrawide + 10MP 3× telephoto",
        battery="4000mAh, 25W wired + 15W wireless",
        pros=["Compact flagship with top chip", "Galaxy AI features", "Bright AMOLED display", "Reliable camera"],
        cons=["Smaller battery", "No charger included", "Competitive with iPhone 16 price"],
        best_for=["compact Android users", "everyday excellence", "Samsung ecosystem"],
        not_for=["heavy gaming", "large battery needs", "S Pen users"],
        tags=["samsung", "galaxy", "s25", "flagship", "5g", "compact", "android"],
        image_url="/images/products/galaxy-s25-1.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 15, One UI 7"), ("Charging", "25W wired + 15W wireless")],
    ),
    PhoneModel(
        brand="Samsung", series="Galaxy S24 Series", model_name="Samsung Galaxy S24 FE",
        ram="8GB", color="Blue",
        storage_variants=[
            ("128GB", 54999), ("256GB", 61999),
        ],
        rating=4.5, ai_score=88,
        display='6.7" Dynamic AMOLED 2X, 120Hz',
        chip="Exynos 2500",
        camera="50MP main + 12MP ultrawide + 8MP 3× telephoto",
        battery="4700mAh, 25W wired",
        pros=["Galaxy AI at mid-range price", "Large bright AMOLED display", "Good camera versatility", "7 years of updates"],
        cons=["Exynos chip vs Snapdragon", "Slower 25W charging", "Plastic frame"],
        best_for=["value Galaxy seekers", "Galaxy AI features on budget", "media consumption"],
        not_for=["top performance seekers", "gaming", "premium build quality"],
        tags=["samsung", "galaxy", "s24", "fe", "5g", "android", "mid-range"],
        image_url="/images/products/galaxy-s25-1.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, One UI 6.1"), ("Charging", "25W wired + 15W wireless")],
    ),
    PhoneModel(
        brand="Samsung", series="Galaxy Z Series", model_name="Samsung Galaxy Z Fold 6",
        ram="12GB", color="Silver Shadow",
        storage_variants=[
            ("256GB", 164999), ("512GB", 184999),
        ],
        rating=4.7, ai_score=94,
        display='7.6" Dynamic AMOLED 2X inner + 6.3" cover display',
        chip="Snapdragon 8 Gen 3",
        camera="50MP main + 12MP ultrawide + 10MP 3× telephoto",
        battery="4400mAh, 25W wired",
        pros=["Tablet + phone in one", "S Pen support (sold separately)", "Galaxy AI multitasking", "Refined fold mechanism"],
        cons=["Very expensive", "Thick when folded", "No charger", "Crease on fold"],
        best_for=["foldable phone enthusiasts", "productivity multitaskers", "early adopters"],
        not_for=["budget buyers", "compact phone users", "gaming-first buyers"],
        tags=["samsung", "galaxy", "fold", "foldable", "5g", "android", "premium"],
        image_url="/images/products/galaxy-s25-1.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, One UI 6.1.1"), ("Form", "Book-fold")],
    ),
    PhoneModel(
        brand="Samsung", series="Galaxy Z Series", model_name="Samsung Galaxy Z Flip 6",
        ram="12GB", color="Crafted Black",
        storage_variants=[
            ("256GB", 109999), ("512GB", 129999),
        ],
        rating=4.6, ai_score=91,
        display='6.7" Dynamic AMOLED 2X inner + 3.4" Flex Window',
        chip="Snapdragon 8 Gen 3",
        camera="50MP main + 12MP ultrawide",
        battery="4000mAh, 25W wired",
        pros=["Compact when folded", "Large Flex Window for quick tasks", "Premium flip design", "Good Snapdragon 8 Gen 3 chip"],
        cons=["Expensive for a flip", "No telephoto", "Smaller battery", "Crease on inner screen"],
        best_for=["fashion-forward users", "those wanting compact fold", "Instagram creators"],
        not_for=["productivity", "pro photography", "budget buyers"],
        tags=["samsung", "galaxy", "flip", "foldable", "5g", "android", "compact"],
        image_url="/images/products/galaxy-s25-1.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, One UI 6.1"), ("Form", "Flip-fold")],
    ),
    PhoneModel(
        brand="Samsung", series="Galaxy A Series", model_name="Samsung Galaxy A56",
        ram="8GB", color="Awesome Graphite",
        storage_variants=[
            ("128GB", 37999), ("256GB", 41999),
        ],
        rating=4.4, ai_score=85,
        display='6.7" Super AMOLED, 120Hz',
        chip="Exynos 1580",
        camera="50MP main + 12MP ultrawide + 5MP macro",
        battery="5000mAh, 45W wired",
        pros=["Galaxy AI features at mid-range", "Great AMOLED display", "Fast 45W charging", "IP67 water resistance"],
        cons=["Exynos chip limitation", "No optical zoom telephoto", "Plastic body"],
        best_for=["value-for-money seekers", "Samsung ecosystem", "social media content"],
        not_for=["flagship performance", "professional photography", "gaming"],
        tags=["samsung", "galaxy", "a56", "mid-range", "5g", "android", "value"],
        image_url="/images/products/galaxy-s25-1.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 15, One UI 7"), ("Charging", "45W wired + 15W wireless"), ("Water Resistance", "IP67")],
    ),
    PhoneModel(
        brand="Samsung", series="Galaxy A Series", model_name="Samsung Galaxy A36",
        ram="8GB", color="Awesome Lilac",
        storage_variants=[
            ("128GB", 28999),
        ],
        rating=4.3, ai_score=82,
        display='6.7" Super AMOLED, 120Hz',
        chip="Snapdragon 6 Gen 3",
        camera="50MP main + 8MP ultrawide",
        battery="5000mAh, 45W wired",
        pros=["Bright AMOLED at this price", "45W fast charging", "Good Snapdragon chip", "Clean One UI experience"],
        cons=["Limited camera system", "No telephoto", "Plastic build"],
        best_for=["budget Galaxy seekers", "first smartphone buyers", "students"],
        not_for=["camera enthusiasts", "gaming", "pro users"],
        tags=["samsung", "galaxy", "a36", "budget", "5g", "android", "student"],
        image_url="/images/products/galaxy-s25-1.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 15"), ("Charging", "45W wired")],
    ),
    PhoneModel(
        brand="Samsung", series="Galaxy M Series", model_name="Samsung Galaxy M56",
        ram="8GB", color="Teal Blue",
        storage_variants=[
            ("128GB", 25999), ("256GB", 29999),
        ],
        rating=4.3, ai_score=82,
        display='6.7" Super AMOLED, 120Hz',
        chip="Exynos 1480",
        camera="50MP main + 8MP ultrawide",
        battery="6000mAh, 45W wired",
        pros=["Massive 6000mAh battery", "Large AMOLED display", "45W fast charging", "Value positioning"],
        cons=["Exynos chip performance", "Heavy device", "No telephoto"],
        best_for=["heavy users needing battery", "media consumption", "rural connectivity"],
        not_for=["performance gaming", "compact design seekers", "pro photography"],
        tags=["samsung", "galaxy", "m56", "battery", "5g", "android", "value"],
        image_url="/images/products/galaxy-s25-1.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 15"), ("Charging", "45W wired")],
    ),

    # ── Google Pixel ──────────────────────────────────────────────────────────
    PhoneModel(
        brand="Google", series="Pixel 9 Series", model_name="Google Pixel 9 Pro XL",
        ram="16GB", color="Obsidian",
        storage_variants=[
            ("128GB", 114999), ("256GB", 129999), ("512GB", 149999),
        ],
        rating=4.8, ai_score=97,
        display='6.8" LTPO OLED, 1-120Hz',
        chip="Google Tensor G4",
        camera="50MP main + 48MP ultrawide + 48MP 5× telephoto",
        battery="5060mAh, 37W wired + 23W wireless",
        pros=["Best computational photography on Android", "Google AI Overviews & Gemini", "7 years OS updates", "Call Screen & Now Playing AI"],
        cons=["Tensor G4 thermal throttle under load", "Expensive import pricing", "Limited service centres in India"],
        best_for=["Google AI enthusiasts", "photographers", "stock Android lovers", "privacy-conscious users"],
        not_for=["gaming", "buyers needing wide service network", "budget buyers"],
        tags=["google", "pixel", "flagship", "5g", "android", "ai", "camera", "google-ai"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Google_Pixel_9_Pro.jpg/800px-Google_Pixel_9_Pro.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Android 15"), ("Charging", "37W wired + 23W wireless"), ("AI", "Google Gemini Nano")],
    ),
    PhoneModel(
        brand="Google", series="Pixel 9 Series", model_name="Google Pixel 9 Pro",
        ram="16GB", color="Porcelain",
        storage_variants=[
            ("128GB", 109999), ("256GB", 119999),
        ],
        rating=4.8, ai_score=96,
        display='6.3" LTPO OLED, 1-120Hz',
        chip="Google Tensor G4",
        camera="50MP main + 48MP ultrawide + 48MP 5× telephoto",
        battery="4700mAh, 37W wired",
        pros=["Compact Pro form factor", "Excellent Pixel camera magic", "7 years updates", "Google AI features"],
        cons=["Tensor G4 heat issues", "Premium price", "Limited service in India"],
        best_for=["compact flagship seekers", "Google ecosystem users", "AI photography"],
        not_for=["gaming", "budget buyers"],
        tags=["google", "pixel", "pro", "5g", "android", "camera", "compact", "ai"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Google_Pixel_9_Pro.jpg/800px-Google_Pixel_9_Pro.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Android 15"), ("AI", "Gemini Nano")],
    ),
    PhoneModel(
        brand="Google", series="Pixel 9 Series", model_name="Google Pixel 9",
        ram="12GB", color="Wintergreen",
        storage_variants=[
            ("128GB", 79999), ("256GB", 89999),
        ],
        rating=4.7, ai_score=93,
        display='6.3" OLED, 60-120Hz',
        chip="Google Tensor G4",
        camera="50MP main + 48MP ultrawide",
        battery="4700mAh, 27W wired",
        pros=["Great Pixel camera experience", "Google Gemini Live", "Compact size", "7 years OS updates"],
        cons=["No telephoto lens", "Tensor heating concerns", "High India price"],
        best_for=["Google AI features", "everyday photography", "compact flagship"],
        not_for=["telephoto photography", "gaming", "heavy multitasking"],
        tags=["google", "pixel", "5g", "android", "ai", "camera", "compact"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Google_Pixel_9_Pro.jpg/800px-Google_Pixel_9_Pro.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Android 15"), ("AI", "Gemini Nano")],
    ),
    PhoneModel(
        brand="Google", series="Pixel 8 Series", model_name="Google Pixel 8a",
        ram="8GB", color="Bay",
        storage_variants=[
            ("128GB", 52999),
        ],
        rating=4.6, ai_score=88,
        display='6.1" OLED, 60-120Hz',
        chip="Google Tensor G3",
        camera="64MP main + 13MP ultrawide",
        battery="4492mAh, 18W wired",
        pros=["Excellent camera at this price", "7 years OS updates", "Google AI features", "Compact and lightweight"],
        cons=["Slower 18W charging", "Tensor G3 not as efficient", "Mid-range chip performance"],
        best_for=["budget Pixel buyers", "AI camera enthusiasts", "clean Android experience"],
        not_for=["gaming", "heavy multitasking", "pro photography"],
        tags=["google", "pixel", "8a", "mid-range", "5g", "android", "camera", "budget"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Google_Pixel_9_Pro.jpg/800px-Google_Pixel_9_Pro.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Android 14 → 15"), ("AI", "Gemini Nano")],
    ),

    # ── OnePlus ───────────────────────────────────────────────────────────────
    PhoneModel(
        brand="OnePlus", series="OnePlus 13 Series", model_name="OnePlus 13",
        ram="12GB", color="Midnight Ocean",
        storage_variants=[
            ("256GB", 69999), ("512GB", 79999),
        ],
        rating=4.8, ai_score=95,
        display='6.82" LTPO AMOLED, 1-120Hz',
        chip="Snapdragon 8 Elite",
        camera="50MP main (Hasselblad) + 50MP ultrawide + 50MP 3× telephoto",
        battery="6000mAh, 100W wired + 50W wireless",
        pros=["Blazing 100W fast charging", "Hasselblad camera system", "Snapdragon 8 Elite chip", "Clean OxygenOS", "Great value vs Samsung flagship"],
        cons=["OxygenOS still has bloat", "No IP68 in base", "Limited to India and key markets"],
        best_for=["value flagship seekers", "charging speed priority", "Android enthusiasts"],
        not_for=["iOS users", "small phone lovers", "pure photography first"],
        tags=["oneplus", "flagship", "5g", "android", "fast-charging", "hasselblad", "value"],
        image_url="/images/products/oneplus-nord-4-1.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Android 15, OxygenOS 15"), ("Charging", "100W wired + 50W wireless"), ("Camera", "Hasselblad tuned")],
    ),
    PhoneModel(
        brand="OnePlus", series="OnePlus 13 Series", model_name="OnePlus 13R",
        ram="8GB", color="Nebula Noir",
        storage_variants=[
            ("128GB", 42999), ("256GB", 47999),
        ],
        rating=4.7, ai_score=90,
        display='6.78" AMOLED, 120Hz',
        chip="Snapdragon 8 Gen 2",
        camera="50MP main + 8MP ultrawide + 2MP macro",
        battery="5500mAh, 80W wired",
        pros=["80W fast charging", "Snapdragon 8 Gen 2 performance", "Great display quality", "Competitive pricing"],
        cons=["Older Snapdragon 8 Gen 2", "Basic secondary cameras", "No wireless charging"],
        best_for=["value mid-range seekers", "charging speed", "gaming on budget"],
        not_for=["camera enthusiasts", "premium material needs"],
        tags=["oneplus", "mid-range", "5g", "android", "fast-charging", "gaming"],
        image_url="/images/products/oneplus-nord-4-1.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, OxygenOS 14"), ("Charging", "80W wired")],
    ),
    PhoneModel(
        brand="OnePlus", series="Nord 5 Series", model_name="OnePlus Nord 5",
        ram="8GB", color="Aqua Boost",
        storage_variants=[
            ("128GB", 34999), ("256GB", 38999),
        ],
        rating=4.5, ai_score=86,
        display='6.77" AMOLED, 120Hz',
        chip="Snapdragon 7s Gen 3",
        camera="50MP main + 8MP ultrawide",
        battery="5500mAh, 67W wired",
        pros=["Good performance for price", "67W fast charging", "Clean OxygenOS", "4 years OS updates"],
        cons=["Limited camera versatility", "No wireless charging", "Snapdragon 7s tier"],
        best_for=["budget-conscious flagship style buyers", "students", "everyday use"],
        not_for=["gaming extremes", "pro photography", "flagship seekers"],
        tags=["oneplus", "nord", "mid-range", "5g", "android", "value", "student"],
        image_url="/images/products/oneplus-nord-4-1.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Android 15, OxygenOS 15"), ("Charging", "67W wired")],
    ),
    PhoneModel(
        brand="OnePlus", series="Nord CE Series", model_name="OnePlus Nord CE 4",
        ram="8GB", color="Celadon Marble",
        storage_variants=[
            ("128GB", 24999), ("256GB", 27999),
        ],
        rating=4.4, ai_score=83,
        display='6.67" AMOLED FHD+, 120Hz',
        chip="Snapdragon 7s Gen 2",
        camera="50MP main + 8MP ultrawide",
        battery="5500mAh, 100W wired",
        pros=["100W ultra-fast charging at budget price", "Clean AMOLED display", "Lightweight design", "Good battery life"],
        cons=["Snapdragon 7s Gen 2 mid-tier", "Basic camera system", "No telephoto"],
        best_for=["budget fast-charging needs", "light daily use", "college students"],
        not_for=["gaming heavy", "pro cameras", "flagship performance"],
        tags=["oneplus", "nord", "ce", "budget", "5g", "android", "fast-charging"],
        image_url="/images/products/oneplus-nord-4-1.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Android 14"), ("Charging", "100W wired")],
    ),

    # ── Nothing ───────────────────────────────────────────────────────────────
    PhoneModel(
        brand="Nothing", series="Phone 2 Series", model_name="Nothing Phone (2a) Plus",
        ram="12GB", color="Black",
        storage_variants=[
            ("256GB", 24999), ("512GB", 28999),
        ],
        rating=4.6, ai_score=87,
        display='6.7" AMOLED FHD+, 120Hz',
        chip="MediaTek Dimensity 7350 Pro",
        camera="50MP main + 50MP ultrawide",
        battery="5000mAh, 50W wired",
        pros=["Unique Glyph interface lighting", "Clean Nothing OS 3", "50MP ultrawide quality", "Fast 50W charging"],
        cons=["MediaTek mid-range chip", "No telephoto", "Niche Glyph appeal"],
        best_for=["design enthusiasts", "clean Android lovers", "Glyph fans"],
        not_for=["gaming", "pro cameras", "premium performance seekers"],
        tags=["nothing", "phone", "2a", "plus", "5g", "android", "glyph", "design"],
        image_url="/images/products/nothing-phone-2a-1.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Nothing OS 3.0"), ("Charging", "50W wired"), ("Feature", "Glyph Interface")],
    ),
    PhoneModel(
        brand="Nothing", series="Phone 2 Series", model_name="Nothing Phone (2a)",
        ram="8GB", color="Milk",
        storage_variants=[
            ("128GB", 19999), ("256GB", 23999),
        ],
        rating=4.5, ai_score=85,
        display='6.7" AMOLED FHD+, 120Hz',
        chip="MediaTek Dimensity 7200 Pro",
        camera="50MP main + 50MP ultrawide",
        battery="5000mAh, 45W wired",
        pros=["Best value Nothing phone", "Glyph interface", "Clean Nothing OS", "Dual 50MP cameras"],
        cons=["Dimensity 7200 mid-range", "No telephoto", "Glyph novelty wears off"],
        best_for=["budget design lovers", "first-time Nothing buyers", "social media use"],
        not_for=["heavy gaming", "pro camera users", "premium seekers"],
        tags=["nothing", "phone", "2a", "budget", "5g", "android", "glyph", "value"],
        image_url="/images/products/nothing-phone-2a-1.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Nothing OS 3.0"), ("Charging", "45W wired"), ("Feature", "Glyph Interface")],
    ),
    PhoneModel(
        brand="Nothing", series="Phone 2 Series", model_name="Nothing Phone (2)",
        ram="12GB", color="Dark Grey",
        storage_variants=[
            ("256GB", 44999), ("512GB", 54999),
        ],
        rating=4.7, ai_score=91,
        display='6.7" LTPO OLED, 1-120Hz',
        chip="Snapdragon 8+ Gen 1",
        camera="50MP main + 50MP ultrawide",
        battery="4700mAh, 45W wired + 15W wireless",
        pros=["Premium Glyph 2.0 lighting", "Smooth LTPO display", "Wireless charging", "Clean Android 15"],
        cons=["No telephoto", "Older Snapdragon 8+ Gen 1", "Price vs competitors"],
        best_for=["design aficionados", "clean Android", "wireless charging", "unique style"],
        not_for=["telephoto photography", "gaming performance leaders"],
        tags=["nothing", "phone", "2", "premium", "5g", "android", "glyph", "wireless-charging"],
        image_url="/images/products/nothing-phone-2a-1.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Nothing OS 3.0"), ("Charging", "45W wired + 15W wireless"), ("Feature", "Glyph Interface 2.0")],
    ),

    # ── Motorola ──────────────────────────────────────────────────────────────
    PhoneModel(
        brand="Motorola", series="Edge 50 Series", model_name="Motorola Edge 50 Ultra",
        ram="12GB", color="Nordic Wood",
        storage_variants=[
            ("256GB", 59999), ("512GB", 69999),
        ],
        rating=4.7, ai_score=91,
        display='6.67" pOLED, 1-165Hz',
        chip="Snapdragon 8s Gen 3",
        camera="50MP main + 50MP ultrawide + 64MP periscope telephoto",
        battery="4500mAh, 125W wired + 50W wireless",
        pros=["Ultra-fast 125W charging", "Periscope telephoto lens", "Premium vegan leather/wood design", "165Hz smooth display"],
        cons=["Snapdragon 8s Gen 3 not full 8 Elite", "Average battery size for ultra-fast charge", "Moto bloatware"],
        best_for=["charging speed priority", "telephoto photography", "premium design lovers"],
        not_for=["gaming extremes", "budget buyers", "stock Android only"],
        tags=["motorola", "edge", "50", "ultra", "5g", "android", "fast-charging", "periscope"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Motorola_Edge_30_Ultra.jpg/800px-Motorola_Edge_30_Ultra.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, Hello UI"), ("Charging", "125W wired + 50W wireless"), ("Design", "Vegan leather back")],
    ),
    PhoneModel(
        brand="Motorola", series="Edge 50 Series", model_name="Motorola Edge 50 Pro",
        ram="12GB", color="Black Beauty",
        storage_variants=[
            ("256GB", 31999), ("512GB", 36999),
        ],
        rating=4.6, ai_score=88,
        display='6.67" pOLED, 144Hz',
        chip="Snapdragon 7 Gen 3",
        camera="50MP main + 13MP ultrawide + 10MP 3× telephoto",
        battery="4500mAh, 125W wired + 50W wireless",
        pros=["125W lightning fast charging", "pOLED display quality", "Good camera system", "Wireless charging at this price"],
        cons=["Snapdragon 7 Gen 3 mid-tier", "Moto bloatware", "Average gaming performance"],
        best_for=["fast charging lovers", "display quality seekers", "everyday productivity"],
        not_for=["gaming", "flagship chips", "pure performance"],
        tags=["motorola", "edge", "50", "pro", "5g", "android", "fast-charging", "pOLED"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Motorola_Edge_30_Ultra.jpg/800px-Motorola_Edge_30_Ultra.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Android 14"), ("Charging", "125W wired + 50W wireless")],
    ),
    PhoneModel(
        brand="Motorola", series="Edge 50 Series", model_name="Motorola Edge 50 Fusion",
        ram="8GB", color="Hot Pink",
        storage_variants=[
            ("128GB", 21999), ("256GB", 24999),
        ],
        rating=4.4, ai_score=83,
        display='6.7" pOLED FHD+, 144Hz',
        chip="Snapdragon 7s Gen 2",
        camera="50MP main + 13MP ultrawide",
        battery="5000mAh, 68W wired",
        pros=["pOLED display at budget", "IP68 water resistance", "68W fast charging", "Clean Android One-like experience"],
        cons=["Basic Snapdragon 7s", "No telephoto", "Average performance ceiling"],
        best_for=["display quality on budget", "IP68 water resistance need", "everyday use"],
        not_for=["gaming", "telephoto photography", "heavy workloads"],
        tags=["motorola", "edge", "50", "fusion", "budget", "5g", "android", "ip68"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Motorola_Edge_30_Ultra.jpg/800px-Motorola_Edge_30_Ultra.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Android 14"), ("Charging", "68W wired"), ("Water Resistance", "IP68")],
    ),
    PhoneModel(
        brand="Motorola", series="Moto G Series", model_name="Motorola Moto G85",
        ram="8GB", color="Cobalt Blue",
        storage_variants=[
            ("128GB", 17999), ("256GB", 19999),
        ],
        rating=4.3, ai_score=80,
        display='6.67" AMOLED, 120Hz',
        chip="Snapdragon 6s Gen 3",
        camera="50MP main + 8MP ultrawide",
        battery="5000mAh, 33W wired",
        pros=["AMOLED at budget price", "Snapdragon 6s Gen 3", "33W fast charging", "Good everyday camera"],
        cons=["Snapdragon 6s tier", "No telephoto", "Limited gaming"],
        best_for=["budget AMOLED seekers", "students", "basic daily use"],
        not_for=["gaming", "performance tasks", "pro photography"],
        tags=["motorola", "moto", "g85", "budget", "5g", "android", "student", "amoled"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Motorola_Edge_30_Ultra.jpg/800px-Motorola_Edge_30_Ultra.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Android 14"), ("Charging", "33W wired")],
    ),
    PhoneModel(
        brand="Motorola", series="Razr Series", model_name="Motorola Razr 50 Ultra",
        ram="12GB", color="Peach Fuzz",
        storage_variants=[
            ("256GB", 99999),
        ],
        rating=4.6, ai_score=90,
        display='6.9" pOLED inner + 4" Flex View cover',
        chip="Snapdragon 8s Gen 3",
        camera="50MP main + 50MP ultrawide",
        battery="4000mAh, 45W wired + 15W wireless",
        pros=["Large Flex View cover display", "Premium flip design", "Dual 50MP cameras", "Good Moto AI features"],
        cons=["Expensive flip form factor", "Snapdragon 8s not full 8 Elite", "Small battery"],
        best_for=["flip foldable enthusiasts", "fashionable design", "social photography"],
        not_for=["performance gaming", "budget buyers", "large phone users"],
        tags=["motorola", "razr", "flip", "foldable", "5g", "android", "premium", "fashion"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Motorola_Edge_30_Ultra.jpg/800px-Motorola_Edge_30_Ultra.jpg",
        extra_specs=[("Network", "5G"), ("OS", "Android 14"), ("Form", "Flip-fold"), ("Cover Display", "4-inch Flex View")],
    ),

    # ── Xiaomi ────────────────────────────────────────────────────────────────
    PhoneModel(
        brand="Xiaomi", series="Xiaomi 14 Series", model_name="Xiaomi 14 Ultra",
        ram="16GB", color="Titanium Black",
        storage_variants=[
            ("512GB", 99999),
        ],
        rating=4.9, ai_score=97,
        display='6.73" LTPO AMOLED, 1-120Hz',
        chip="Snapdragon 8 Gen 3",
        camera="50MP main (Leica 1-inch) + 50MP ultrawide + 50MP 3.2× + 50MP 5× periscope",
        battery="5000mAh, 90W wired + 80W wireless",
        pros=["Leica quad-camera system with 1-inch sensor", "Variable aperture main lens", "Top Snapdragon 8 Gen 3", "Versatile 4-camera setup"],
        cons=["Very expensive", "Large and heavy", "MIUI/HyperOS bloatware", "Limited India availability"],
        best_for=["photography enthusiasts", "Leica quality seekers", "Android flagship lovers"],
        not_for=["budget buyers", "iOS loyalists", "compact phone seekers"],
        tags=["xiaomi", "14", "ultra", "flagship", "5g", "android", "leica", "periscope", "camera"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Xiaomi_logo_%282021%29.svg/800px-Xiaomi_logo_%282021%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, HyperOS"), ("Charging", "90W wired + 80W wireless"), ("Camera", "Leica 1-inch sensor with variable aperture")],
    ),
    PhoneModel(
        brand="Xiaomi", series="Xiaomi 14 Series", model_name="Xiaomi 14",
        ram="12GB", color="Jade Green",
        storage_variants=[
            ("256GB", 69999), ("512GB", 79999),
        ],
        rating=4.8, ai_score=94,
        display='6.36" LTPO AMOLED, 1-120Hz',
        chip="Snapdragon 8 Gen 3",
        camera="50MP main (Leica) + 50MP ultrawide + 50MP 3.2× telephoto",
        battery="4610mAh, 90W wired + 50W wireless",
        pros=["Compact flagship with Leica cameras", "Snapdragon 8 Gen 3 performance", "90W ultra-fast charging", "IP68 rated"],
        cons=["Expensive for India", "HyperOS ads and bloat", "Small battery relative to size"],
        best_for=["compact flagship seekers", "Leica photography", "charging speed"],
        not_for=["large screen lovers", "stock Android users", "budget buyers"],
        tags=["xiaomi", "14", "flagship", "5g", "android", "leica", "compact", "ip68"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Xiaomi_logo_%282021%29.svg/800px-Xiaomi_logo_%282021%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, HyperOS"), ("Charging", "90W wired + 50W wireless"), ("Water Resistance", "IP68")],
    ),

    # ── Redmi ─────────────────────────────────────────────────────────────────
    PhoneModel(
        brand="Xiaomi", series="Redmi Note 14 Series", model_name="Redmi Note 14 Pro+",
        ram="12GB", color="Phantom Purple",
        storage_variants=[
            ("256GB", 29999), ("512GB", 34999),
        ],
        rating=4.7, ai_score=89,
        display='6.67" AMOLED, 120Hz',
        chip="MediaTek Dimensity 9200+",
        camera="200MP main + 8MP ultrawide + 2MP macro",
        battery="5110mAh, 120W wired + 10W wireless",
        pros=["200MP camera at mid-range", "120W ultra-fast charging", "Dimensity 9200+ flagship chip", "IP68 water resistance"],
        cons=["MediaTek chip not for everyone", "Software bloat", "No telephoto optical zoom"],
        best_for=["camera enthusiasts on budget", "fast charging", "water resistant needs"],
        not_for=["gaming extremes", "pure stock Android", "telephoto needs"],
        tags=["redmi", "note", "14", "pro", "plus", "5g", "android", "camera", "fast-charging"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Xiaomi_logo_%282021%29.svg/800px-Xiaomi_logo_%282021%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, HyperOS"), ("Charging", "120W wired + 10W wireless"), ("Water Resistance", "IP68")],
    ),
    PhoneModel(
        brand="Xiaomi", series="Redmi Note 14 Series", model_name="Redmi Note 14 Pro",
        ram="8GB", color="Midnight Black",
        storage_variants=[
            ("128GB", 21999), ("256GB", 24999),
        ],
        rating=4.6, ai_score=86,
        display='6.67" AMOLED, 120Hz',
        chip="MediaTek Dimensity 7300 Ultra",
        camera="108MP main + 8MP ultrawide",
        battery="5500mAh, 45W wired",
        pros=["108MP camera at this price", "Large battery with fast charging", "Good AMOLED display", "IP68 certified"],
        cons=["Dimensity 7300 mid-tier", "No telephoto", "MIUI ads"],
        best_for=["camera quality on budget", "battery life", "everyday use"],
        not_for=["gaming", "performance workloads", "stock Android seekers"],
        tags=["redmi", "note", "14", "pro", "5g", "android", "camera", "battery"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Xiaomi_logo_%282021%29.svg/800px-Xiaomi_logo_%282021%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, HyperOS"), ("Charging", "45W wired"), ("Water Resistance", "IP68")],
    ),
    PhoneModel(
        brand="Xiaomi", series="Redmi Note 14 Series", model_name="Redmi Note 14",
        ram="6GB", color="Midnight Blue",
        storage_variants=[
            ("128GB", 16999),
        ],
        rating=4.4, ai_score=81,
        display='6.67" AMOLED, 120Hz',
        chip="Snapdragon 4s Gen 2",
        camera="108MP main + 2MP depth",
        battery="5500mAh, 33W wired",
        pros=["AMOLED at entry-level price", "108MP camera", "Large 5500mAh battery", "5G connectivity"],
        cons=["Snapdragon 4s entry-level", "Basic secondary cameras", "Slow 33W charging for size"],
        best_for=["first 5G buyers", "budget AMOLED seekers", "students on tight budget"],
        not_for=["gaming", "pro photography", "performance tasks"],
        tags=["redmi", "note", "14", "budget", "5g", "android", "student", "amoled"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Xiaomi_logo_%282021%29.svg/800px-Xiaomi_logo_%282021%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, HyperOS"), ("Charging", "33W wired")],
    ),
    PhoneModel(
        brand="Xiaomi", series="Redmi 14 Series", model_name="Redmi 14C",
        ram="4GB", color="Dreamy Purple",
        storage_variants=[
            ("128GB", 9999), ("256GB", 11999),
        ],
        rating=4.1, ai_score=73,
        display='6.88" IPS LCD, 90Hz',
        chip="MediaTek Helio G85",
        camera="50MP main + 0.08MP depth",
        battery="5160mAh, 18W wired",
        pros=["Ultra affordable 5G", "Large LCD display", "Good battery life", "Decent camera for the price"],
        cons=["Entry-level Helio G85", "LCD display", "No 5G on base model", "Very basic specs"],
        best_for=["ultra-budget buyers", "first smartphone users", "rural connectivity"],
        not_for=["any performance task", "gaming", "camera enthusiasts"],
        tags=["redmi", "14c", "budget", "android", "entry-level", "affordable"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Xiaomi_logo_%282021%29.svg/800px-Xiaomi_logo_%282021%29.svg.png",
        extra_specs=[("Network", "4G/5G"), ("OS", "Android 14, HyperOS"), ("Charging", "18W wired")],
    ),

    # ── POCO ──────────────────────────────────────────────────────────────────
    PhoneModel(
        brand="Xiaomi", series="POCO X7 Series", model_name="POCO X7 Pro",
        ram="12GB", color="Jade Green",
        storage_variants=[
            ("256GB", 26999), ("512GB", 30999),
        ],
        rating=4.6, ai_score=87,
        display='6.67" AMOLED, 120Hz',
        chip="MediaTek Dimensity 8400 Ultra",
        camera="50MP main + 8MP ultrawide",
        battery="6550mAh, 90W wired",
        pros=["Dimensity 8400 Ultra chip at mid-range", "90W fast charging", "Massive 6550mAh battery", "Good AMOLED display"],
        cons=["Basic camera system", "MIUI/HyperOS bloat", "No telephoto", "POCO brand perception"],
        best_for=["gaming enthusiasts", "battery life priority", "value performance"],
        not_for=["camera quality", "premium brand seekers", "bloat-free experience"],
        tags=["poco", "x7", "pro", "gaming", "5g", "android", "battery", "fast-charging", "value"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Xiaomi_logo_%282021%29.svg/800px-Xiaomi_logo_%282021%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 15, HyperOS 2"), ("Charging", "90W wired")],
    ),
    PhoneModel(
        brand="Xiaomi", series="POCO X7 Series", model_name="POCO X7",
        ram="8GB", color="Black",
        storage_variants=[
            ("256GB", 21999),
        ],
        rating=4.4, ai_score=83,
        display='6.67" AMOLED, 120Hz',
        chip="MediaTek Dimensity 7300 Ultra",
        camera="50MP main + 8MP ultrawide",
        battery="5110mAh, 45W wired",
        pros=["AMOLED at budget price", "Good daily performance", "5G connectivity", "IP64 splashproof"],
        cons=["Dimensity 7300 mid-tier", "45W only charging", "Basic cameras"],
        best_for=["value AMOLED seekers", "everyday 5G", "budget gaming"],
        not_for=["heavy gaming", "pro photography", "pro-grade features"],
        tags=["poco", "x7", "mid-range", "5g", "android", "value", "amoled"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Xiaomi_logo_%282021%29.svg/800px-Xiaomi_logo_%282021%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, HyperOS"), ("Charging", "45W wired")],
    ),
    PhoneModel(
        brand="Xiaomi", series="POCO M6 Series", model_name="POCO M6 Pro",
        ram="8GB", color="Snowstorm White",
        storage_variants=[
            ("128GB", 13999), ("256GB", 15999),
        ],
        rating=4.2, ai_score=77,
        display='6.67" AMOLED, 120Hz',
        chip="MediaTek Dimensity 6080",
        camera="64MP main + 8MP ultrawide + 2MP macro",
        battery="5000mAh, 67W wired",
        pros=["67W fast charging at very low price", "AMOLED display", "64MP camera", "Good value"],
        cons=["Dimensity 6080 entry-level", "Limited performance ceiling", "Software bloat"],
        best_for=["ultra budget AMOLED", "fast charging on budget", "first-time buyers"],
        not_for=["gaming", "performance workloads", "premium experience"],
        tags=["poco", "m6", "pro", "budget", "5g", "android", "fast-charging", "amoled", "value"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Xiaomi_logo_%282021%29.svg/800px-Xiaomi_logo_%282021%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 13, MIUI 14"), ("Charging", "67W wired")],
    ),

    # ── Realme ────────────────────────────────────────────────────────────────
    PhoneModel(
        brand="Realme", series="GT 6 Series", model_name="Realme GT 6",
        ram="12GB", color="Fluid Silver",
        storage_variants=[
            ("256GB", 35999), ("512GB", 40999),
        ],
        rating=4.7, ai_score=91,
        display='6.78" AMOLED, 120Hz BOE ProXDR',
        chip="Snapdragon 8s Gen 3",
        camera="50MP main + 8MP ultrawide + 50MP 3× telephoto",
        battery="5500mAh, 120W wired",
        pros=["Snapdragon 8s Gen 3 at mid-range", "120W ultra-fast charging", "Bright ProXDR display", "50MP telephoto"],
        cons=["Realme UI has ads", "Snapdragon 8s not full Gen 3", "Large device"],
        best_for=["performance value seekers", "charging speed", "gaming on budget"],
        not_for=["stock Android", "compact size", "premium brand status"],
        tags=["realme", "gt", "6", "5g", "android", "gaming", "fast-charging", "snapdragon"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Realme_logo.svg/800px-Realme_logo.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, Realme UI 5.0"), ("Charging", "120W wired")],
    ),
    PhoneModel(
        brand="Realme", series="GT 6 Series", model_name="Realme GT 6T",
        ram="8GB", color="Razor Green",
        storage_variants=[
            ("128GB", 26999), ("256GB", 30999),
        ],
        rating=4.5, ai_score=87,
        display='6.78" AMOLED, 120Hz',
        chip="Snapdragon 7+ Gen 3",
        camera="50MP main + 8MP ultrawide",
        battery="5500mAh, 120W wired",
        pros=["120W charging at budget", "Snapdragon 7+ Gen 3 chip", "Good AMOLED display", "Fast daily performance"],
        cons=["No telephoto", "Realme UI bloat", "Average cameras in low light"],
        best_for=["value performance", "fast charging priority", "everyday gaming"],
        not_for=["pro cameras", "premium build", "stock Android"],
        tags=["realme", "gt", "6t", "mid-range", "5g", "android", "fast-charging", "gaming"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Realme_logo.svg/800px-Realme_logo.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, Realme UI 5.0"), ("Charging", "120W wired")],
    ),
    PhoneModel(
        brand="Realme", series="Realme 13 Series", model_name="Realme 13 Pro+",
        ram="12GB", color="Monet Purple",
        storage_variants=[
            ("256GB", 32999), ("512GB", 37999),
        ],
        rating=4.6, ai_score=88,
        display='6.7" AMOLED, 120Hz',
        chip="Snapdragon 7s Gen 2",
        camera="50MP main (Sony LYT-701) + 8MP ultrawide + 50MP 3× telephoto",
        battery="5200mAh, 80W wired",
        pros=["Sony LYT-701 sensor quality", "50MP telephoto at this price", "80W fast charging", "Good portrait photography"],
        cons=["Snapdragon 7s Gen 2 mid-tier", "Realme UI ads", "Average video quality"],
        best_for=["camera quality seekers", "portrait photography", "80W fast charging"],
        not_for=["gaming performance", "stock Android", "heavy workloads"],
        tags=["realme", "13", "pro", "plus", "5g", "android", "camera", "telephoto", "sony-sensor"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Realme_logo.svg/800px-Realme_logo.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, Realme UI 5.0"), ("Charging", "80W wired"), ("Camera Sensor", "Sony LYT-701")],
    ),
    PhoneModel(
        brand="Realme", series="Realme 13 Series", model_name="Realme 13 Pro",
        ram="8GB", color="Emerald Green",
        storage_variants=[
            ("256GB", 27999),
        ],
        rating=4.5, ai_score=85,
        display='6.7" AMOLED, 120Hz',
        chip="Snapdragon 7s Gen 2",
        camera="50MP main + 8MP ultrawide",
        battery="5200mAh, 67W wired",
        pros=["Good AMOLED display", "67W fast charging", "Solid everyday performance", "Slim design"],
        cons=["No telephoto", "Mid-tier chip", "Realme UI bloat"],
        best_for=["value mid-range", "everyday use", "display quality seekers"],
        not_for=["gaming", "pro cameras", "premium build"],
        tags=["realme", "13", "pro", "mid-range", "5g", "android", "value"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Realme_logo.svg/800px-Realme_logo.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, Realme UI 5.0"), ("Charging", "67W wired")],
    ),
    PhoneModel(
        brand="Realme", series="Narzo Series", model_name="Realme Narzo 70 Pro",
        ram="8GB", color="Glass Gold",
        storage_variants=[
            ("256GB", 22999),
        ],
        rating=4.3, ai_score=81,
        display='6.67" AMOLED, 120Hz',
        chip="MediaTek Dimensity 7050",
        camera="50MP main + 8MP ultrawide",
        battery="5000mAh, 67W wired",
        pros=["AMOLED at competitive price", "67W fast charging", "IP54 splash resistance", "5G ready"],
        cons=["Dimensity 7050 mid-tier", "No telephoto", "Realme UI ads"],
        best_for=["AMOLED on budget", "everyday 5G users", "students"],
        not_for=["gaming", "pro photography", "premium segment"],
        tags=["realme", "narzo", "70", "pro", "budget", "5g", "android", "amoled"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Realme_logo.svg/800px-Realme_logo.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, Realme UI 5.0"), ("Charging", "67W wired")],
    ),

    # ── OPPO ──────────────────────────────────────────────────────────────────
    PhoneModel(
        brand="Oppo", series="Find X8 Series", model_name="OPPO Find X8 Pro",
        ram="16GB", color="Space Black",
        storage_variants=[
            ("256GB", 89999), ("512GB", 99999),
        ],
        rating=4.8, ai_score=95,
        display='6.78" LTPO AMOLED, 1-120Hz',
        chip="MediaTek Dimensity 9400",
        camera="50MP main + 50MP ultrawide + 50MP 3× + 50MP 6× periscope (Hasselblad)",
        battery="5910mAh, 80W wired + 50W wireless",
        pros=["Hasselblad quad-camera excellence", "Dimensity 9400 top performance", "Large 5910mAh battery", "80W fast charging with wireless"],
        cons=["Very expensive for India", "ColorOS bloatware", "Limited service centres"],
        best_for=["Hasselblad photography", "video creators", "long battery day", "premium Android"],
        not_for=["budget buyers", "iOS ecosystem", "small size lovers"],
        tags=["oppo", "find", "x8", "pro", "5g", "android", "hasselblad", "flagship", "periscope"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/OPPO_LOGO_2019.svg/800px-OPPO_LOGO_2019.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 15, ColorOS 15"), ("Charging", "80W wired + 50W wireless"), ("Camera", "Hasselblad tuned")],
    ),
    PhoneModel(
        brand="Oppo", series="Find X8 Series", model_name="OPPO Find X8",
        ram="12GB", color="Pearl White",
        storage_variants=[
            ("256GB", 64999), ("512GB", 74999),
        ],
        rating=4.7, ai_score=93,
        display='6.59" AMOLED, 120Hz',
        chip="MediaTek Dimensity 9400",
        camera="50MP main + 50MP ultrawide + 50MP 3× telephoto (Hasselblad)",
        battery="5630mAh, 80W wired + 50W wireless",
        pros=["Dimensity 9400 flagship chip", "Hasselblad camera quality", "Large battery", "Compact vs Pro"],
        cons=["Expensive import pricing", "ColorOS bloat", "No periscope telephoto"],
        best_for=["flagship camera performance", "Hasselblad lovers", "battery life priority"],
        not_for=["budget buyers", "stock Android preference"],
        tags=["oppo", "find", "x8", "5g", "android", "hasselblad", "flagship"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/OPPO_LOGO_2019.svg/800px-OPPO_LOGO_2019.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 15, ColorOS 15"), ("Charging", "80W wired + 50W wireless")],
    ),
    PhoneModel(
        brand="Oppo", series="Reno 13 Series", model_name="OPPO Reno 13 Pro",
        ram="12GB", color="Luminous Blue",
        storage_variants=[
            ("256GB", 39999),
        ],
        rating=4.5, ai_score=86,
        display='6.83" OLED, 120Hz',
        chip="MediaTek Dimensity 8350",
        camera="50MP main (Sony LYT-600) + 8MP ultrawide + 50MP 3× telephoto",
        battery="5800mAh, 80W wired",
        pros=["Large 5800mAh battery", "Sony sensor quality", "50MP telephoto", "Slim premium design"],
        cons=["Dimensity 8350 mid-tier", "ColorOS bloat", "Average video quality"],
        best_for=["battery life", "portrait photography", "everyday premium feel"],
        not_for=["flagship chip performance", "stock Android", "gaming first"],
        tags=["oppo", "reno", "13", "pro", "mid-range", "5g", "android", "camera", "telephoto"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/OPPO_LOGO_2019.svg/800px-OPPO_LOGO_2019.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 15, ColorOS 15"), ("Charging", "80W wired")],
    ),
    PhoneModel(
        brand="Oppo", series="Reno 13 Series", model_name="OPPO Reno 13",
        ram="8GB", color="Graphite Grey",
        storage_variants=[
            ("256GB", 31999),
        ],
        rating=4.4, ai_score=83,
        display='6.59" AMOLED, 120Hz',
        chip="MediaTek Dimensity 8350",
        camera="50MP main + 8MP ultrawide",
        battery="5600mAh, 45W wired",
        pros=["Large AMOLED display", "Good battery capacity", "Slim and lightweight", "IP65 splash resistance"],
        cons=["No telephoto", "45W charging only", "Limited gaming performance"],
        best_for=["daily use", "battery life", "slim design lovers"],
        not_for=["gaming", "pro photography", "flagship seekers"],
        tags=["oppo", "reno", "13", "mid-range", "5g", "android", "battery"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/OPPO_LOGO_2019.svg/800px-OPPO_LOGO_2019.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 15, ColorOS 15"), ("Charging", "45W wired")],
    ),

    # ── Vivo ──────────────────────────────────────────────────────────────────
    PhoneModel(
        brand="Vivo", series="X200 Series", model_name="Vivo X200 Pro",
        ram="16GB", color="Titanium Grey",
        storage_variants=[
            ("256GB", 89999), ("512GB", 99999),
        ],
        rating=4.8, ai_score=95,
        display='6.78" LTPO AMOLED, 1-120Hz',
        chip="MediaTek Dimensity 9400",
        camera="50MP main + 50MP ultrawide + 200MP 3.7× periscope telephoto (ZEISS)",
        battery="6000mAh, 90W wired + 30W wireless",
        pros=["200MP ZEISS periscope telephoto", "Dimensity 9400 top performance", "6000mAh large battery", "90W fast charging"],
        cons=["Expensive in India", "Funtouch OS bloat", "Large and heavy"],
        best_for=["telephoto photography", "battery life priority", "video creators", "ZEISS optics"],
        not_for=["budget buyers", "compact phones", "stock Android users"],
        tags=["vivo", "x200", "pro", "flagship", "5g", "android", "zeiss", "periscope", "200mp"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Vivo_logo_%282019%29.svg/800px-Vivo_logo_%282019%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 15, Funtouch OS 15"), ("Charging", "90W wired + 30W wireless"), ("Camera", "ZEISS T* coating")],
    ),
    PhoneModel(
        brand="Vivo", series="X200 Series", model_name="Vivo X200",
        ram="12GB", color="Cosmos Black",
        storage_variants=[
            ("256GB", 62999), ("512GB", 72999),
        ],
        rating=4.7, ai_score=92,
        display='6.67" AMOLED, 120Hz',
        chip="MediaTek Dimensity 9400",
        camera="50MP main (ZEISS) + 50MP ultrawide + 50MP 2× telephoto",
        battery="5800mAh, 90W wired + 30W wireless",
        pros=["ZEISS camera quality", "Dimensity 9400 chip", "Large 5800mAh battery", "Slim design"],
        cons=["No periscope telephoto vs Pro", "Funtouch OS bloat", "Expensive"],
        best_for=["camera quality", "battery life", "everyday flagship use"],
        not_for=["long telephoto photography", "budget buyers"],
        tags=["vivo", "x200", "flagship", "5g", "android", "zeiss", "battery"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Vivo_logo_%282019%29.svg/800px-Vivo_logo_%282019%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 15, Funtouch OS 15"), ("Charging", "90W wired + 30W wireless")],
    ),
    PhoneModel(
        brand="Vivo", series="V40 Series", model_name="Vivo V40 Pro",
        ram="8GB", color="Ganges Blue",
        storage_variants=[
            ("256GB", 39999),
        ],
        rating=4.6, ai_score=87,
        display='6.78" AMOLED, 120Hz',
        chip="Snapdragon 7 Gen 3",
        camera="50MP main (ZEISS) + 50MP ultrawide + 50MP 2× telephoto",
        battery="5500mAh, 80W wired",
        pros=["Triple 50MP ZEISS cameras", "80W fast charging", "Good Snapdragon 7 Gen 3", "Slim design"],
        cons=["No telephoto zoom quality vs periscope", "Funtouch bloat", "Average gaming performance"],
        best_for=["camera triple-lens quality", "everyday premium style", "portrait photography"],
        not_for=["gaming first", "pure performance seekers"],
        tags=["vivo", "v40", "pro", "mid-range", "5g", "android", "zeiss", "camera"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Vivo_logo_%282019%29.svg/800px-Vivo_logo_%282019%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, Funtouch OS 14"), ("Charging", "80W wired")],
    ),
    PhoneModel(
        brand="Vivo", series="V40 Series", model_name="Vivo V40",
        ram="8GB", color="Lotus Purple",
        storage_variants=[
            ("128GB", 29999), ("256GB", 33999),
        ],
        rating=4.5, ai_score=84,
        display='6.78" AMOLED, 120Hz',
        chip="Snapdragon 7 Gen 3",
        camera="50MP main (ZEISS) + 50MP ultrawide",
        battery="5500mAh, 80W wired",
        pros=["ZEISS dual cameras at mid-range", "80W charging", "Bright AMOLED", "Good everyday performance"],
        cons=["No telephoto", "Funtouch OS bloat", "Average low light"],
        best_for=["everyday camera quality", "mid-range value", "battery and charging"],
        not_for=["telephoto photography", "gaming", "stock Android"],
        tags=["vivo", "v40", "mid-range", "5g", "android", "zeiss", "camera"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Vivo_logo_%282019%29.svg/800px-Vivo_logo_%282019%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, Funtouch OS 14"), ("Charging", "80W wired")],
    ),
    PhoneModel(
        brand="Vivo", series="T Series", model_name="Vivo T3 Pro",
        ram="8GB", color="Sunset Bliss",
        storage_variants=[
            ("128GB", 22999), ("256GB", 26999),
        ],
        rating=4.4, ai_score=83,
        display='6.78" AMOLED, 144Hz',
        chip="Snapdragon 7 Gen 3",
        camera="50MP main + 8MP ultrawide",
        battery="5000mAh, 80W wired",
        pros=["144Hz AMOLED display", "80W fast charging", "Snapdragon 7 Gen 3", "Good gaming performance"],
        best_for=["gaming enthusiasts on budget", "fast charging", "display quality"],
        cons=["No telephoto", "Funtouch bloat", "Mid-range camera quality"],
        not_for=["pro photography", "stock Android"],
        tags=["vivo", "t3", "pro", "gaming", "mid-range", "5g", "android", "fast-charging"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Vivo_logo_%282019%29.svg/800px-Vivo_logo_%282019%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14"), ("Charging", "80W wired")],
    ),

    # ── iQOO ──────────────────────────────────────────────────────────────────
    PhoneModel(
        brand="Vivo", series="iQOO 13 Series", model_name="iQOO 13",
        ram="16GB", color="Legend",
        storage_variants=[
            ("256GB", 54999), ("512GB", 64999),
        ],
        rating=4.9, ai_score=97,
        display='6.82" AMOLED, 144Hz',
        chip="Snapdragon 8 Elite",
        camera="50MP main + 50MP ultrawide + 50MP 2× telephoto",
        battery="6150mAh, 120W wired + 30W wireless",
        pros=["Snapdragon 8 Elite at competitive price", "120W ultra-fast charging", "144Hz gaming display", "Excellent gaming performance", "Large 6150mAh battery"],
        cons=["Basic iQOO UI", "Limited brand recognition", "Three 50MP cameras lack variety", "Flagship gaming focus may not suit all"],
        best_for=["competitive mobile gaming", "performance enthusiasts", "value flagship"],
        not_for=["iOS users", "budget buyers", "telephoto photography needs"],
        tags=["iqoo", "13", "flagship", "gaming", "5g", "android", "snapdragon", "fast-charging", "value"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Vivo_logo_%282019%29.svg/800px-Vivo_logo_%282019%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 15, FunTouch OS 15"), ("Charging", "120W wired + 30W wireless"), ("Gaming", "Vapour chamber cooling")],
    ),
    PhoneModel(
        brand="Vivo", series="iQOO 12 Series", model_name="iQOO 12",
        ram="12GB", color="Legend",
        storage_variants=[
            ("256GB", 52999), ("512GB", 59999),
        ],
        rating=4.8, ai_score=95,
        display='6.78" AMOLED, 144Hz',
        chip="Snapdragon 8 Gen 3",
        camera="50MP main + 50MP ultrawide + 64MP 3× telephoto",
        battery="5000mAh, 120W wired + 50W wireless",
        pros=["Snapdragon 8 Gen 3 at competitive price", "120W + 50W wireless charging", "Good camera versatility", "144Hz gaming display"],
        cons=["Previous flagship chip now", "iQOO UI feels bloated", "Battery smaller than iQOO 13"],
        best_for=["performance gaming", "value flagship seekers", "charging speed enthusiasts"],
        not_for=["camera-first buyers", "budget segment", "iOS users"],
        tags=["iqoo", "12", "flagship", "gaming", "5g", "android", "snapdragon", "fast-charging"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Vivo_logo_%282019%29.svg/800px-Vivo_logo_%282019%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, FunTouch OS 14"), ("Charging", "120W wired + 50W wireless")],
    ),
    PhoneModel(
        brand="Vivo", series="iQOO Neo Series", model_name="iQOO Neo 9 Pro",
        ram="12GB", color="Fiery Red",
        storage_variants=[
            ("256GB", 34999), ("512GB", 39999),
        ],
        rating=4.7, ai_score=91,
        display='6.78" AMOLED, 144Hz',
        chip="Snapdragon 8 Gen 2",
        camera="50MP main + 8MP ultrawide",
        battery="5160mAh, 80W wired",
        pros=["Snapdragon 8 Gen 2 at this price", "144Hz gaming display", "80W fast charging", "Gaming focused cooling"],
        cons=["Older 8 Gen 2 chip now", "Basic dual cameras", "iQOO UI"],
        best_for=["gaming on budget", "performance seekers", "fast charging"],
        not_for=["pro photography", "camera versatility", "compact design"],
        tags=["iqoo", "neo", "9", "pro", "gaming", "mid-range", "5g", "android", "snapdragon"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Vivo_logo_%282019%29.svg/800px-Vivo_logo_%282019%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14"), ("Charging", "80W wired")],
    ),
    PhoneModel(
        brand="Vivo", series="iQOO Z Series", model_name="iQOO Z9 Pro",
        ram="8GB", color="Brushed Green",
        storage_variants=[
            ("128GB", 22999), ("256GB", 25999),
        ],
        rating=4.5, ai_score=86,
        display='6.77" AMOLED, 144Hz',
        chip="MediaTek Dimensity 9300+",
        camera="50MP main + 8MP ultrawide",
        battery="5500mAh, 66W wired",
        pros=["Dimensity 9300+ at budget", "144Hz AMOLED gaming display", "66W fast charging", "Good gaming performance"],
        cons=["Basic camera system", "No telephoto", "iQOO UI ads"],
        best_for=["gaming on budget", "AMOLED display quality", "value performance"],
        not_for=["pro photography", "premium design seekers", "stock Android"],
        tags=["iqoo", "z9", "pro", "gaming", "budget", "5g", "android", "amoled"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Vivo_logo_%282019%29.svg/800px-Vivo_logo_%282019%29.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14"), ("Charging", "66W wired")],
    ),

    # ── Honor ──────────────────────────────────────────────────────────────────
    PhoneModel(
        brand="Honor", series="Magic 6 Series", model_name="Honor Magic 6 Pro",
        ram="12GB", color="Monet Edition",
        storage_variants=[
            ("512GB", 74999),
        ],
        rating=4.7, ai_score=93,
        display='6.8" LTPO OLED, 1-120Hz',
        chip="Snapdragon 8 Gen 3",
        camera="50MP main + 50MP ultrawide + 180MP 3.5× periscope telephoto",
        battery="5600mAh, 80W wired + 66W wireless",
        pros=["180MP periscope telephoto", "Snapdragon 8 Gen 3", "80W wired + 66W wireless", "Premium design", "Excellent long zoom capability"],
        cons=["High price", "MagicOS may not suit all", "Limited India service"],
        best_for=["telephoto photography enthusiasts", "premium Android seekers", "wireless charging lovers"],
        not_for=["budget buyers", "stock Android users"],
        tags=["honor", "magic", "6", "pro", "flagship", "5g", "android", "periscope", "180mp"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/HONOR_logo.svg/800px-HONOR_logo.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, MagicOS 8"), ("Charging", "80W wired + 66W wireless")],
    ),
    PhoneModel(
        brand="Honor", series="Honor 200 Series", model_name="Honor 200 Pro",
        ram="12GB", color="Midnight Black",
        storage_variants=[
            ("256GB", 44999), ("512GB", 54999),
        ],
        rating=4.6, ai_score=89,
        display='6.78" OLED, 120Hz',
        chip="Snapdragon 8s Gen 3",
        camera="50MP main + 50MP ultrawide + 50MP 2.5× telephoto (Harcourt Studio)",
        battery="5200mAh, 100W wired + 66W wireless",
        pros=["Harcourt Studio portrait photography", "100W ultra-fast charging + 66W wireless", "Triple 50MP cameras", "Good Snapdragon 8s Gen 3"],
        cons=["Snapdragon 8s not full 8 Elite", "MagicOS learning curve", "Limited India brand presence"],
        best_for=["portrait photography", "fast charging lovers", "wireless charging", "premium mid-range"],
        not_for=["stock Android", "gaming extremes", "budget buyers"],
        tags=["honor", "200", "pro", "mid-range", "5g", "android", "portrait", "fast-charging"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/HONOR_logo.svg/800px-HONOR_logo.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, MagicOS 8"), ("Charging", "100W wired + 66W wireless"), ("Camera", "Harcourt Studio tuned")],
    ),
    PhoneModel(
        brand="Honor", series="Honor 200 Series", model_name="Honor 200",
        ram="8GB", color="Starry Blue",
        storage_variants=[
            ("256GB", 34999),
        ],
        rating=4.5, ai_score=86,
        display='6.7" OLED, 120Hz',
        chip="Snapdragon 7 Gen 3",
        camera="50MP main + 12MP ultrawide + 50MP 2.5× telephoto",
        battery="5000mAh, 100W wired",
        pros=["100W fast charging at this price", "Triple camera with telephoto", "Good OLED display", "Harcourt portrait mode"],
        cons=["Snapdragon 7 Gen 3 mid-tier", "No wireless charging vs Pro", "Limited service network"],
        best_for=["portrait camera quality", "fast charging", "value mid-range"],
        not_for=["gaming performance", "flagship chip seekers"],
        tags=["honor", "200", "mid-range", "5g", "android", "camera", "fast-charging"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/HONOR_logo.svg/800px-HONOR_logo.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 14, MagicOS 8"), ("Charging", "100W wired")],
    ),
    PhoneModel(
        brand="Honor", series="Honor X Series", model_name="Honor X9b",
        ram="8GB", color="Titanium Black",
        storage_variants=[
            ("256GB", 22999),
        ],
        rating=4.3, ai_score=80,
        display='6.78" AMOLED, 90Hz',
        chip="Snapdragon 6 Gen 1",
        camera="108MP main + 5MP ultrawide",
        battery="5800mAh, 35W wired",
        pros=["Large 5800mAh battery", "108MP camera at this price", "IP53 splashproof", "Durable military-grade build"],
        cons=["Snapdragon 6 Gen 1 mid-tier", "90Hz only", "No telephoto", "Limited camera quality"],
        best_for=["battery life priority", "rugged daily use", "budget 5G buyers"],
        not_for=["gaming", "pro photography", "premium performance"],
        tags=["honor", "x9b", "budget", "5g", "android", "battery", "durable"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/HONOR_logo.svg/800px-HONOR_logo.svg.png",
        extra_specs=[("Network", "5G"), ("OS", "Android 13, MagicOS 7.2"), ("Charging", "35W wired"), ("Build", "Military-grade drop tested")],
    ),
]


# ── Insertion logic ───────────────────────────────────────────────────────────

def run() -> None:
    session = SessionLocal()
    try:
        # Get "smartphones" category (or fall back to "phone")
        smartphone_cat = session.scalars(
            select(Category).where(Category.slug == "smartphones")
        ).first()
        if not smartphone_cat:
            smartphone_cat = session.scalars(
                select(Category).where(Category.slug == "phone")
            ).first()
        if not smartphone_cat:
            print("ERROR: Could not find 'smartphones' or 'phone' category. Run migrations first.")
            return

        print(f"Seeding into category: {smartphone_cat.name} (slug={smartphone_cat.slug})")

        # Build brand map (get or create)
        brand_cache: dict[str, Brand] = {}
        unique_brands = {p.brand for p in PHONES}
        for brand_name in unique_brands:
            existing = session.scalars(select(Brand).where(Brand.name == brand_name)).first()
            if existing:
                brand_cache[brand_name] = existing
            else:
                b = Brand(name=brand_name, slug=slugify(brand_name))
                session.add(b)
                session.flush()
                brand_cache[brand_name] = b

        inserted = 0
        skipped = 0

        for phone in PHONES:
            brand = brand_cache[phone.brand]

            for storage, price_inr in phone.storage_variants:
                # Strip brand prefix from model name to avoid double-slug (e.g., "samsung-samsung-galaxy")
                model_for_slug = phone.model_name
                if model_for_slug.lower().startswith(phone.brand.lower()):
                    model_for_slug = model_for_slug[len(phone.brand):].strip()
                slug = slugify(f"{phone.brand}-{model_for_slug}-{storage}")

                # Skip duplicates
                exists = session.scalars(select(Product).where(Product.slug == slug)).first()
                if exists:
                    skipped += 1
                    continue

                description = (
                    f"{phone.model_name} is a {phone.chip}-powered smartphone in the {phone.series} lineup. "
                    f"It features a {phone.display} display with {storage} storage and {phone.ram} RAM. "
                    f"The camera system packs {phone.camera}. Battery: {phone.battery}."
                )

                product = Product(
                    slug=slug,
                    name=f"{phone.model_name} {storage}",
                    description=description,
                    availability=phone.availability,
                    category_id=smartphone_cat.id,
                    brand_id=brand.id,
                    price_value=inr(price_inr),
                    currency="INR",
                    rating=Decimal(str(phone.rating)),
                    ai_score=phone.ai_score,
                    ai_summary=(
                        f"{phone.model_name} scores {phone.ai_score}/100. "
                        f"Powered by {phone.chip}, it excels in {phone.best_for[0]}. "
                        f"Highlight: {phone.pros[0]}."
                    ),
                    review_summary=(
                        f"Users love the {phone.pros[0].lower()}. "
                        f"Most common concern: {phone.cons[0].lower()}."
                    ),
                    series=phone.series,
                    model_name=phone.model_name,
                    variant=f"{storage} / {phone.ram} RAM / {phone.color}",
                    storage=storage,
                    ram=phone.ram,
                    color=phone.color,
                )
                session.add(product)
                session.flush()

                # Image
                session.add(ProductImage(product_id=product.id, url=phone.image_url, position=1))

                # Specifications
                specs = [
                    ("Display", phone.display),
                    ("Chip", phone.chip),
                    ("Camera", phone.camera),
                    ("Battery", phone.battery),
                    ("Storage", storage),
                    ("RAM", phone.ram),
                    ("Color", phone.color),
                    ("OS", "iOS 18" if phone.brand == "Apple" else "Android 14/15"),
                    ("Network", "5G"),
                ]
                specs.extend(phone.extra_specs)
                seen_labels: set[str] = set()
                for pos, (label, value) in enumerate(specs, start=1):
                    if label not in seen_labels:
                        session.add(ProductSpecification(product_id=product.id, label=label, value=value, position=pos))
                        seen_labels.add(label)

                # Features
                features = [
                    phone.display,
                    phone.chip,
                    phone.camera,
                    phone.battery,
                    f"{storage} internal storage",
                    f"{phone.ram} RAM",
                ]
                for pos, feat in enumerate(features[:6], start=1):
                    session.add(ProductFeature(product_id=product.id, value=feat, position=pos))

                # Pros / cons
                for pos, pro in enumerate(phone.pros[:5], start=1):
                    session.add(ProductPro(product_id=product.id, value=pro, position=pos))
                for pos, con in enumerate(phone.cons[:3], start=1):
                    session.add(ProductCon(product_id=product.id, value=con, position=pos))

                # Best for / not for
                for pos, v in enumerate(phone.best_for[:3], start=1):
                    session.add(ProductBestFor(product_id=product.id, value=v, position=pos))
                for pos, v in enumerate(phone.not_for[:2], start=1):
                    session.add(ProductNotRecommendedFor(product_id=product.id, value=v, position=pos))

                # Tags
                all_tags = {
                    smartphone_cat.slug, slugify(phone.brand),
                    "smartphone", "mobile", "5g",
                    *phone.tags,
                    slugify(phone.model_name),
                }
                for tag in all_tags:
                    session.add(ProductTag(product_id=product.id, value=tag))

                # Price history (6-month trend)
                base = price_inr
                for label, mult in [("Jan", 1.06), ("Feb", 1.04), ("Mar", 1.02), ("Apr", 1.01), ("May", 1.0), ("Now", 1.0)]:
                    session.add(PriceHistory(
                        product_id=product.id,
                        label=label,
                        price=inr(round(base * mult / 100) * 100),
                    ))

                # Reviews
                review_data = [
                    ("Great purchase, exactly as described.", 4.5),
                    ("Camera quality is impressive for the price.", 5.0),
                    ("Battery lasts a full day easily.", 4.5),
                    (f"{phone.cons[0]} is a real concern.", 3.5),
                    ("Would definitely recommend to a friend.", 4.5),
                ]
                review_names = ["Arjun S.", "Priya K.", "Rahul M.", "Sneha T.", "Vikram P."]
                review_dates = ["2026-03-15", "2026-04-20", "2026-05-10", "2026-06-05", "2026-07-12"]
                review_titles = [
                    "Excellent daily driver",
                    "Best phone I've owned",
                    "Worth every rupee",
                    "Good with minor trade-offs",
                    "Highly recommended",
                ]
                for i, ((comment, r), name, date, title) in enumerate(zip(review_data, review_names, review_dates, review_titles)):
                    session.add(Review(
                        product_id=product.id,
                        author=name,
                        title=title,
                        rating=Decimal(str(r)),
                        comment=comment,
                        date=date,
                    ))

                inserted += 1

        session.commit()
        print(f"\n✓ Done. Inserted: {inserted} | Skipped (already existed): {skipped}")
        print(f"  Category: {smartphone_cat.name} (id={smartphone_cat.id})")

        # Print summary
        brands_covered = sorted({p.brand for p in PHONES})
        models_covered = sorted({p.model_name for p in PHONES})
        total_skus = sum(len(p.storage_variants) for p in PHONES)
        print(f"\n  Brands ({len(brands_covered)}): {', '.join(brands_covered)}")
        print(f"  Unique models: {len(models_covered)}")
        print(f"  Total SKUs defined: {total_skus}")

    except Exception as exc:
        session.rollback()
        print(f"ERROR: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run()
