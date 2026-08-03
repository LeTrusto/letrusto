"""
Phase 2 – Hosting & SaaS catalog seed.
Seeds 20 web hosting and SaaS products into 'web-hosting' category.
Run standalone: python -m scripts.seed_hosting_saas
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from decimal import Decimal

sys.path.insert(0, ".")

from sqlalchemy import select

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


@dataclass
class HostingProduct:
    brand: str
    name: str
    slug_suffix: str
    price_inr_month: int
    billing: str          # "monthly" | "annual" | "one-time"
    rating: float
    ai_score: int
    category: str          # "web-hosting" | "saas"
    tagline: str
    pros: list[str]
    cons: list[str]
    best_for: list[str]
    not_for: list[str]
    specs: list[tuple[str, str]]
    tags: list[str]
    image_url: str
    affiliate_url: str


PRODUCTS: list[HostingProduct] = [
    # ── Web Hosting ──────────────────────────────────────────────────────────
    HostingProduct(
        brand="Hostinger", name="Hostinger Starter", slug_suffix="starter",
        price_inr_month=69, billing="annual",
        rating=4.7, ai_score=93,
        category="web-hosting",
        tagline="Best budget web hosting for beginners",
        pros=["Cheapest reliable hosting", "Free domain 1st year", "Easy WordPress installer", "99.9% uptime guarantee"],
        cons=["Shared resources", "No phone support", "Renewal price higher"],
        best_for=["bloggers", "beginners", "small websites"],
        not_for=["high-traffic stores", "enterprise", "complex apps"],
        specs=[("Storage", "100 GB SSD"), ("Bandwidth", "Unlimited"), ("Websites", "1"), ("Email", "1 account"), ("SSL", "Free"), ("Panel", "hPanel")],
        tags=["hosting", "web-hosting", "beginner", "cheap", "wordpress"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Hostinger_logo_2023.svg/1280px-Hostinger_logo_2023.svg.png",
        affiliate_url="https://www.hostinger.in/web-hosting",
    ),
    HostingProduct(
        brand="Hostinger", name="Hostinger Business", slug_suffix="business",
        price_inr_month=179, billing="annual",
        rating=4.8, ai_score=96,
        category="web-hosting",
        tagline="Best all-round hosting for growing websites",
        pros=["Unlimited websites", "Free domain", "Free CDN", "Daily backups", "Fast LiteSpeed servers"],
        cons=["No VPS", "Limited to shared environment"],
        best_for=["small businesses", "freelancers", "ecommerce startups"],
        not_for=["large traffic sites", "dedicated server needs"],
        specs=[("Storage", "200 GB SSD"), ("Bandwidth", "Unlimited"), ("Websites", "100"), ("Email", "100 accounts"), ("SSL", "Free Wildcard"), ("CDN", "Cloudflare included")],
        tags=["hosting", "web-hosting", "business", "wordpress", "ecommerce", "recommended"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Hostinger_logo_2023.svg/1280px-Hostinger_logo_2023.svg.png",
        affiliate_url="https://www.hostinger.in/web-hosting",
    ),
    HostingProduct(
        brand="Hostinger", name="Hostinger Cloud Startup", slug_suffix="cloud",
        price_inr_month=649, billing="annual",
        rating=4.8, ai_score=95,
        category="web-hosting",
        tagline="Managed cloud hosting for faster performance",
        pros=["Dedicated resources", "Faster than shared", "Free domain", "Priority support", "Auto-scaling"],
        cons=["Expensive for beginners", "Overkill for small sites"],
        best_for=["high-traffic websites", "agencies", "performance priority"],
        not_for=["beginners", "budget buyers"],
        specs=[("vCPU", "3 cores"), ("RAM", "3 GB"), ("Storage", "200 GB NVMe"), ("Bandwidth", "Unlimited"), ("SSL", "Free Wildcard")],
        tags=["hosting", "cloud-hosting", "premium", "fast", "performance"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Hostinger_logo_2023.svg/1280px-Hostinger_logo_2023.svg.png",
        affiliate_url="https://www.hostinger.in/cloud-hosting",
    ),
    HostingProduct(
        brand="Bluehost", name="Bluehost Basic", slug_suffix="basic",
        price_inr_month=199, billing="annual",
        rating=4.4, ai_score=84,
        category="web-hosting",
        tagline="Official WordPress recommended hosting",
        pros=["WordPress official partner", "Free domain 1st year", "24/7 support", "Easy cPanel"],
        cons=["Slower than Hostinger", "Expensive renewal", "Upsells on checkout"],
        best_for=["WordPress sites", "beginners wanting brand trust", "US/global audience"],
        not_for=["budget-only buyers", "India-first audience"],
        specs=[("Storage", "10 GB SSD"), ("Websites", "1"), ("SSL", "Free"), ("Panel", "cPanel"), ("Email", "5 accounts")],
        tags=["hosting", "web-hosting", "wordpress", "bluehost"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Bluehost.png/1280px-Bluehost.png",
        affiliate_url="https://www.bluehost.in/",
    ),
    HostingProduct(
        brand="Namecheap", name="Namecheap Stellar", slug_suffix="stellar",
        price_inr_month=83, billing="annual",
        rating=4.5, ai_score=86,
        category="web-hosting",
        tagline="Affordable hosting + free WHOIS privacy",
        pros=["Free WHOIS privacy", "Very affordable", "3 websites on basic", "Good performance"],
        cons=["Basic dashboard", "Limited scalability"],
        best_for=["domain + hosting bundle", "privacy-conscious users", "freelancers"],
        not_for=["high-traffic", "enterprise needs"],
        specs=[("Storage", "20 GB SSD"), ("Websites", "3"), ("SSL", "Free"), ("Bandwidth", "Unmetered"), ("WHOIS Privacy", "Free")],
        tags=["hosting", "web-hosting", "namecheap", "cheap", "domain"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Namecheap_logo.svg/1280px-Namecheap_logo.svg.png",
        affiliate_url="https://www.namecheap.com/hosting/",
    ),

    # ── SaaS Tools ───────────────────────────────────────────────────────────
    HostingProduct(
        brand="Semrush", name="Semrush Pro", slug_suffix="pro",
        price_inr_month=9167, billing="monthly",
        rating=4.8, ai_score=96,
        category="web-hosting",
        tagline="Best all-in-one SEO tool for professionals",
        pros=["Industry-leading keyword research", "Site audit", "Competitor analysis", "Backlink tracking", "PPC research"],
        cons=["Expensive for beginners", "Overwhelming for casual users", "Limited historical data on free"],
        best_for=["SEO professionals", "digital marketers", "content agencies"],
        not_for=["casual bloggers", "ultra-tight budgets", "non-SEO businesses"],
        specs=[("Keywords", "10,000 per report"), ("Projects", "5"), ("Crawl", "100k pages/month"), ("Reports", "3,000/day"), ("Users", "1")],
        tags=["seo", "saas", "semrush", "marketing", "keyword-research"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Semrush_logo.svg/1280px-Semrush_logo.svg.png",
        affiliate_url="https://www.semrush.com/",
    ),
    HostingProduct(
        brand="Canva", name="Canva Pro", slug_suffix="pro",
        price_inr_month=333, billing="annual",
        rating=4.8, ai_score=95,
        category="web-hosting",
        tagline="Best design tool for non-designers",
        pros=["Huge template library", "Brand kit", "Background remover", "Magic AI tools", "Team collaboration"],
        cons=["Can't replace Adobe for pro designers", "Some templates feel generic"],
        best_for=["social media creators", "small businesses", "freelancers", "marketers"],
        not_for=["professional print designers", "complex vector work"],
        specs=[("Templates", "100M+"), ("Brand Kits", "Unlimited"), ("Storage", "1 TB"), ("Magic AI", "Included"), ("Team", "Up to 5")],
        tags=["design", "saas", "canva", "social-media", "ai-design"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Canva_icon_2021.svg/1280px-Canva_icon_2021.svg.png",
        affiliate_url="https://www.canva.com/pro/",
    ),
    HostingProduct(
        brand="Grammarly", name="Grammarly Premium", slug_suffix="premium",
        price_inr_month=300, billing="annual",
        rating=4.7, ai_score=91,
        category="web-hosting",
        tagline="AI writing assistant trusted by millions",
        pros=["Real-time grammar checking", "Tone suggestions", "Plagiarism checker", "Works everywhere in browser"],
        cons=["Expensive renewal", "Occasional false suggestions", "Not for code"],
        best_for=["writers", "students", "professionals", "content creators"],
        not_for=["casual writers", "non-English content"],
        specs=[("Languages", "English"), ("Tone Detector", "Yes"), ("Plagiarism", "Yes"), ("Browser Extension", "Chrome/Firefox/Edge"), ("Mobile", "iOS & Android")],
        tags=["writing", "saas", "grammarly", "ai-writing", "grammar"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Grammarly_logo.svg/1280px-Grammarly_logo.svg.png",
        affiliate_url="https://www.grammarly.com/premium",
    ),
    HostingProduct(
        brand="Notion", name="Notion Plus", slug_suffix="plus",
        price_inr_month=800, billing="annual",
        rating=4.7, ai_score=92,
        category="web-hosting",
        tagline="All-in-one workspace for notes, docs, and projects",
        pros=["Flexible all-in-one workspace", "Great for teams", "AI-powered writing", "Free personal tier available"],
        cons=["Learning curve", "Offline support limited", "Can be slow with large databases"],
        best_for=["students", "remote teams", "freelancers", "project management"],
        not_for=["offline-heavy workflows", "complex spreadsheet needs"],
        specs=[("Blocks", "Unlimited"), ("File Uploads", "Unlimited"), ("Guests", "100"), ("AI", "Optional add-on"), ("API", "Included")],
        tags=["productivity", "saas", "notion", "notes", "project-management"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Notion-logo.svg/1280px-Notion-logo.svg.png",
        affiliate_url="https://www.notion.so/product",
    ),
    HostingProduct(
        brand="NordVPN", name="NordVPN 2-Year Plan", slug_suffix="2year",
        price_inr_month=254, billing="annual",
        rating=4.7, ai_score=90,
        category="web-hosting",
        tagline="Most trusted VPN for privacy and security",
        pros=["Fast servers worldwide", "No-log policy", "Double VPN", "Works with Netflix/streaming", "6 devices"],
        cons=["Expensive monthly plan", "Occasional connection drops"],
        best_for=["privacy-conscious users", "streaming", "remote workers", "travellers"],
        not_for=["free VPN seekers", "basic browsing only"],
        specs=[("Servers", "6000+ in 60 countries"), ("Devices", "6 simultaneous"), ("Protocol", "NordLynx/OpenVPN"), ("Logs", "Zero"), ("Kill Switch", "Yes")],
        tags=["vpn", "security", "saas", "nordvpn", "privacy"],
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/NordVPN_logo_symbol.svg/1280px-NordVPN_logo_symbol.svg.png",
        affiliate_url="https://nordvpn.com/",
    ),
]


def run() -> None:
    session = SessionLocal()
    try:
        # Get or create web-hosting category
        cat = session.scalars(select(Category).where(Category.slug == "web-hosting")).first()
        if not cat:
            cat = Category(name="Web Hosting & SaaS", slug="web-hosting", icon="🌐", position=20)
            session.add(cat)
            session.flush()

        inserted = 0
        skipped = 0

        for p in PRODUCTS:
            # Get or create brand
            brand = session.scalars(select(Brand).where(Brand.name == p.brand)).first()
            if not brand:
                brand = Brand(name=p.brand, slug=slugify(p.brand))
                session.add(brand)
                session.flush()

            slug = slugify(f"{p.brand}-{p.name}-{p.slug_suffix}")
            exists = session.scalars(select(Product).where(Product.slug == slug)).first()
            if exists:
                skipped += 1
                continue

            product = Product(
                slug=slug,
                name=p.name,
                description=p.tagline + f". Starting at ₹{p.price_inr_month}/month ({p.billing} billing).",
                availability="In Stock",
                category_id=cat.id,
                brand_id=brand.id,
                price_value=Decimal(str(p.price_inr_month)),
                currency="INR",
                rating=Decimal(str(p.rating)),
                ai_score=p.ai_score,
                ai_summary=f"{p.name} scores {p.ai_score}/100. {p.tagline}. Best for {p.best_for[0]}.",
                review_summary=f"Users love {p.pros[0].lower()}. Main concern: {p.cons[0].lower()}.",
            )
            session.add(product)
            session.flush()

            session.add(ProductImage(product_id=product.id, url=p.image_url, position=1))

            for pos, (label, value) in enumerate(p.specs, start=1):
                session.add(ProductSpecification(product_id=product.id, label=label, value=value, position=pos))

            for pos, feat in enumerate([p.tagline] + p.pros[:4], start=1):
                session.add(ProductFeature(product_id=product.id, value=feat, position=pos))

            for pos, pro in enumerate(p.pros[:5], start=1):
                session.add(ProductPro(product_id=product.id, value=pro, position=pos))

            for pos, con in enumerate(p.cons[:3], start=1):
                session.add(ProductCon(product_id=product.id, value=con, position=pos))

            for pos, bf in enumerate(p.best_for[:3], start=1):
                session.add(ProductBestFor(product_id=product.id, value=bf, position=pos))

            for pos, nf in enumerate(p.not_for[:2], start=1):
                session.add(ProductNotRecommendedFor(product_id=product.id, value=nf, position=pos))

            for tag in {cat.slug, slugify(p.brand), "hosting", "saas", *p.tags}:
                session.add(ProductTag(product_id=product.id, value=tag))

            # Price history (annual vs monthly)
            base = p.price_inr_month
            for label, mult in [("Jan", 1.1), ("Feb", 1.08), ("Mar", 1.05), ("Apr", 1.02), ("May", 1.0), ("Now", 1.0)]:
                session.add(PriceHistory(product_id=product.id, label=label, price=Decimal(str(round(base * mult)))))

            review_entries = [
                ("Great tool, worth every rupee.", 5.0),
                ("Improved my workflow significantly.", 4.5),
                ("Good value for the features offered.", 4.5),
                (f"{p.cons[0]} is a downside.", 3.5),
                ("Would recommend to colleagues.", 5.0),
            ]
            names = ["Rohit K.", "Priya S.", "Ananya M.", "Kiran P.", "Suresh R."]
            dates = ["2026-04-10", "2026-05-15", "2026-06-08", "2026-06-25", "2026-07-20"]
            titles = ["Excellent service", "Worth the price", "Reliable and fast", "Good with minor issues", "Highly recommended"]
            for (comment, rating), name, date, title in zip(review_entries, names, dates, titles):
                session.add(Review(product_id=product.id, author=name, title=title, rating=Decimal(str(rating)), comment=comment, date=date))

            inserted += 1

        session.commit()
        print(f"✓ Hosting/SaaS seed done. Inserted: {inserted} | Skipped: {skipped}", flush=True)

    except Exception as exc:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run()
