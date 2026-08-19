from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from urllib.parse import urlparse

from app.core.config import Settings, get_settings


LETRUSTO_TAXONOMY = {
    "jewellery": "Jewellery",
    "hair-style": "Hair & Style",
    "beauty-tools": "Beauty Tools",
    "accessories": "Fashion Accessories",
    "gifts": "Gifts",
    "home-kitchen": "Home & Kitchen",
    "fitness": "Fitness",
    "baby-care": "Baby & Kids",
    "pet-care": "Pet Care",
}

# Intentionally starts empty: CJ category IDs must be reviewed before mapping.
CJ_CATEGORY_ID_MAP: dict[str, str] = {}
CJ_CATEGORY_PATH_MAP: dict[str, str] = {}
CATEGORY_MAPPING_VERSION = "v1"
ALLOWED_IMAGE_HOSTS = frozenset({"cf.cjdropshipping.com", "oss-cf.cjdropshipping.com"})


@dataclass(frozen=True)
class CategoryResolution:
    category_slug: str | None
    status: str
    source: str | None
    mapping_version: str = CATEGORY_MAPPING_VERSION


def resolve_cj_category(category_id: str | None, category_path: str | None) -> CategoryResolution:
    if category_id and category_id in CJ_CATEGORY_ID_MAP:
        return CategoryResolution(CJ_CATEGORY_ID_MAP[category_id], "MAPPED", "CJ_CATEGORY_ID")
    normalized_path = " > ".join(part.strip().lower() for part in (category_path or "").split(">") if part.strip())
    if normalized_path and normalized_path in CJ_CATEGORY_PATH_MAP:
        return CategoryResolution(CJ_CATEGORY_PATH_MAP[normalized_path], "MAPPED", "CJ_CATEGORY_PATH")
    return CategoryResolution(None, "REVIEW_REQUIRED", None)


@dataclass(frozen=True)
class BrandResolution:
    status: str
    brand_name: str | None = None


def resolve_brand(*, explicit_brand: str | None, manufacturer: str | None = None) -> BrandResolution:
    value = (explicit_brand or "").strip()
    if value.lower() in {"generic", "unbranded", "no brand", "none"}:
        return BrandResolution("GENERIC", "Generic / Unbranded")
    if value:
        return BrandResolution("BRAND_REVIEW_REQUIRED", value)
    if manufacturer and manufacturer.strip():
        return BrandResolution("BRAND_REVIEW_REQUIRED", manufacturer.strip())
    return BrandResolution("BRAND_REVIEW_REQUIRED")


@dataclass(frozen=True)
class CatalogPricingPolicy:
    pricing_fx_rate: Decimal
    payment_fee_pct: Decimal
    rto_reserve_pct: Decimal
    target_margin_pct: Decimal
    tax_treatment: str = "NOT_CONFIGURED"
    tax_rate_pct: Decimal | None = None

    def validate(self) -> None:
        if self.pricing_fx_rate <= 0:
            raise ValueError("Pricing FX rate must be greater than zero")
        percentages = (self.payment_fee_pct, self.rto_reserve_pct, self.target_margin_pct)
        if any(value < 0 or value >= Decimal("100") for value in percentages):
            raise ValueError("Pricing percentages must be between zero and 100")
        if self.tax_treatment == "NOT_CONFIGURED":
            raise ValueError("Tax treatment is not configured")
        if self.tax_rate_pct is None or self.tax_rate_pct < 0:
            raise ValueError("Tax rate is required for the configured tax treatment")
        if sum(percentages) >= Decimal("100"):
            raise ValueError("Payment fee, RTO reserve, and target margin must total less than 100%")

    @property
    def denominator(self) -> Decimal:
        return Decimal("1") - (self.payment_fee_pct + self.rto_reserve_pct + self.target_margin_pct) / Decimal("100")


def load_catalog_pricing_policy(settings: Settings | None = None) -> CatalogPricingPolicy:
    config = settings or get_settings()
    return CatalogPricingPolicy(
        pricing_fx_rate=config.PRICING_FX_RATE,
        payment_fee_pct=config.PAYMENT_GATEWAY_PCT,
        rto_reserve_pct=config.RTO_RESERVE_PCT,
        target_margin_pct=config.TARGET_CONTRIBUTION_MARGIN_PCT,
        tax_treatment=config.CATALOG_TAX_TREATMENT,
        tax_rate_pct=config.CATALOG_TAX_RATE_PCT,
    )


def is_allowed_image_url(url: str | None) -> bool:
    if not url or not url.strip():
        return False
    parsed = urlparse(url.strip())
    return parsed.scheme == "https" and parsed.hostname in ALLOWED_IMAGE_HOSTS


def is_inventory_stale(last_sync: datetime | None, *, now: datetime | None = None, max_age_minutes: int = 30) -> bool:
    if last_sync is None:
        return True
    current = now or datetime.now(timezone.utc)
    if last_sync.tzinfo is None:
        last_sync = last_sync.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc) - last_sync.astimezone(timezone.utc) > timedelta(minutes=max_age_minutes)
