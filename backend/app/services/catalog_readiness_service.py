from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from app.core.catalog_readiness import is_allowed_image_url, is_inventory_stale, resolve_brand
from app.models.entities import Product


@dataclass(frozen=True)
class ActivationReadiness:
    ready: bool
    blocking_reasons: tuple[str, ...]


class CatalogReadinessService:
    @staticmethod
    def validate_activation(product: Product) -> ActivationReadiness:
        reasons: list[str] = []
        if not product.supplier:
            reasons.append("SUPPLIER_MISSING")
        if not product.supplier_product_id:
            reasons.append("SUPPLIER_PRODUCT_ID_MISSING")
        if not product.name or not product.name.strip():
            reasons.append("PRODUCT_NAME_MISSING")
        if not product.description or not product.description.strip():
            reasons.append("DESCRIPTION_MISSING")
        if product.category_id is None:
            reasons.append("CATEGORY_REVIEW_REQUIRED")
        if product.brand_id is None:
            reasons.append("BRAND_REVIEW_REQUIRED")
        valid_images = [image for image in product.images if is_allowed_image_url(image.url)]
        if not valid_images:
            reasons.append("PRIMARY_IMAGE_INVALID")
        active_variants = [variant for variant in product.variants if variant.active]
        if not active_variants:
            reasons.append("ACTIVE_VARIANT_MISSING")
        for variant in active_variants:
            if not variant.supplier_variant_id:
                reasons.append("SUPPLIER_VARIANT_ID_MISSING")
            if not variant.supplier_variant_sku:
                reasons.append("SUPPLIER_VARIANT_SKU_MISSING")
            if variant.selling_price is None or variant.selling_price <= 0:
                reasons.append("VARIANT_PRICE_INVALID")
        if active_variants and not any((variant.cj_inventory or 0) > 0 for variant in active_variants):
            reasons.append("NO_SELLABLE_INVENTORY")
        if product.shipping_cost is None or product.shipping_cost < 0:
            reasons.append("SHIPPING_COST_MISSING")
        if product.commercial_status != "APPROVED":
            reasons.append("COMMERCIAL_REVIEW_REQUIRED")
        if product.supplier_validation_status in {None, "REVIEW", "REJECT"}:
            reasons.append("SUPPLIER_VALIDATION_NOT_APPROVED")
        if is_inventory_stale(product.last_supplier_sync_at):
            reasons.append("INVENTORY_SYNC_STALE")
        return ActivationReadiness(ready=not reasons, blocking_reasons=tuple(dict.fromkeys(reasons)))

    @staticmethod
    def classify_brand(*, explicit_brand: str | None, manufacturer: str | None = None) -> str:
        return resolve_brand(explicit_brand=explicit_brand, manufacturer=manufacturer).status

    @staticmethod
    def validate_image_urls(urls: list[str]) -> tuple[str, ...]:
        return tuple(url for url in urls if not is_allowed_image_url(url))

    @staticmethod
    def display_price(product: Product) -> Decimal | None:
        prices = [variant.selling_price for variant in product.variants if variant.active and variant.selling_price is not None and variant.selling_price > 0]
        return min(prices) if prices else None

    @staticmethod
    def classify_reimport(existing: Product | None, supplier: str, supplier_product_id: str) -> str:
        if existing is None:
            return "NEW_DRAFT"
        if existing.status == "DRAFT":
            return "UPDATE_DRAFT_SOURCE_FIELDS"
        if existing.status == "ACTIVE":
            return "ACTIVE_REVIEW_REQUIRED"
        return "UPDATE_NON_ACTIVE_SOURCE_FIELDS"
