"""Normalize raw supplier products into a supplier-independent format."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.suppliers.base import RawSupplierProduct, RawVariant

# USD → INR rate. In production this would come from a config or API.
DEFAULT_USD_TO_INR = 83.5


class ProductStatus(str, Enum):
    IMPORTED = "IMPORTED"
    NORMALIZED = "NORMALIZED"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"


@dataclass
class NormalizedVariant:
    variant_id: str
    supplier_variant_id: str
    supplier_variant_sku: str
    name: str
    option_key: str
    image: str = ""
    cost_usd: float | None = None
    cost_inr: float | None = None
    weight_grams: float | None = None
    length_mm: int | None = None
    width_mm: int | None = None
    height_mm: int | None = None
    inventory: int | None = None
    warehouse_country: str = ""
    barcode: str = ""


@dataclass
class NormalizedProduct:
    """Supplier-independent product representation."""

    letrusto_product_id: str
    supplier_id: str
    supplier_product_id: str
    supplier_sku: str
    title: str
    description: str
    images: list[str] = field(default_factory=list)
    video_urls: list[str] = field(default_factory=list)
    category: str = ""
    supplier_category_id: str = ""
    cost_usd: float | None = None
    cost_inr: float | None = None
    currency: str = "INR"
    weight_grams: float | None = None
    packing_weight_grams: float | None = None
    variants: list[NormalizedVariant] = field(default_factory=list)
    total_inventory: int | None = None
    warehouse_country: str = ""
    delivery_cycle_days: str = ""
    logistics_properties: list[str] = field(default_factory=list)
    status: ProductStatus = ProductStatus.IMPORTED
    missing_fields: list[str] = field(default_factory=list)


def normalize_product(
    raw: RawSupplierProduct,
    *,
    usd_to_inr: float = DEFAULT_USD_TO_INR,
) -> NormalizedProduct:
    missing: list[str] = []
    if not raw.title:
        missing.append("title")
    if raw.price_usd is None:
        missing.append("price")
    if not raw.images:
        missing.append("images")
    if raw.weight_grams is None:
        missing.append("weight")
    if raw.inventory_total is None:
        missing.append("inventory")
    if not raw.category_name:
        missing.append("category")

    cost_inr = round(raw.price_usd * usd_to_inr, 2) if raw.price_usd is not None else None

    variants = [_normalize_variant(v, usd_to_inr=usd_to_inr) for v in raw.variants]

    lt_id = f"lt-{raw.supplier_id}-{raw.supplier_product_id[:12]}"

    return NormalizedProduct(
        letrusto_product_id=lt_id,
        supplier_id=raw.supplier_id,
        supplier_product_id=raw.supplier_product_id,
        supplier_sku=raw.supplier_sku,
        title=raw.title,
        description=raw.description,
        images=raw.images,
        video_urls=raw.video_urls,
        category=raw.category_name,
        supplier_category_id=raw.category_id,
        cost_usd=raw.price_usd,
        cost_inr=cost_inr,
        weight_grams=raw.weight_grams,
        packing_weight_grams=raw.packing_weight_grams,
        variants=variants,
        total_inventory=raw.inventory_total,
        warehouse_country=raw.warehouse_country,
        delivery_cycle_days=raw.delivery_cycle_days,
        logistics_properties=raw.logistics_properties,
        status=ProductStatus.NORMALIZED,
        missing_fields=missing,
    )


def _normalize_variant(raw: RawVariant, *, usd_to_inr: float) -> NormalizedVariant:
    cost_inr = round(raw.price_usd * usd_to_inr, 2) if raw.price_usd is not None else None
    return NormalizedVariant(
        variant_id=f"ltv-{raw.supplier_variant_id[:12]}",
        supplier_variant_id=raw.supplier_variant_id,
        supplier_variant_sku=raw.supplier_variant_sku,
        name=raw.name,
        option_key=raw.option_key,
        image=raw.image,
        cost_usd=raw.price_usd,
        cost_inr=cost_inr,
        weight_grams=raw.weight_grams,
        length_mm=raw.length_mm,
        width_mm=raw.width_mm,
        height_mm=raw.height_mm,
        inventory=raw.inventory,
        warehouse_country=raw.warehouse_country,
        barcode=raw.barcode,
    )
