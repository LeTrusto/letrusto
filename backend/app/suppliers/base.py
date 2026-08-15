"""Supplier adapter protocol — supplier-agnostic interface."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, runtime_checkable


class ShippingValidation(str, Enum):
    VERIFIED = "VERIFIED"
    REQUIRES_MANUAL_VALIDATION = "REQUIRES_MANUAL_VALIDATION"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    UNKNOWN = "UNKNOWN"


@dataclass
class InventorySnapshot:
    total_inventory: int
    cj_inventory: int
    factory_inventory: int
    verification_status: str | None = None


@dataclass
class RawSupplierProduct:
    """Unprocessed product data exactly as the supplier returns it."""

    supplier_id: str
    supplier_product_id: str
    supplier_sku: str
    title: str
    description: str = ""
    images: list[str] = field(default_factory=list)
    video_urls: list[str] = field(default_factory=list)
    category_name: str = ""
    category_id: str = ""
    price_usd: float | None = None
    currency: str = "USD"
    weight_grams: float | None = None
    packing_weight_grams: float | None = None
    variants: list[RawVariant] = field(default_factory=list)
    inventory_total: int | None = None
    total_inventory: int | None = None
    cj_inventory: int | None = None
    factory_inventory: int | None = None
    inventory_verification: str | None = None
    warehouse_country: str = ""
    delivery_cycle_days: str = ""
    logistics_properties: list[str] = field(default_factory=list)
    raw_payload: dict | None = None


@dataclass
class RawVariant:
    supplier_variant_id: str
    supplier_variant_sku: str
    name: str = ""
    option_key: str = ""
    image: str = ""
    price_usd: float | None = None
    weight_grams: float | None = None
    length_mm: int | None = None
    width_mm: int | None = None
    height_mm: int | None = None
    inventory: int | None = None
    total_inventory: int | None = None
    cj_inventory: int | None = None
    factory_inventory: int | None = None
    inventory_verification: str | None = None
    warehouse_country: str = ""
    barcode: str = ""


@dataclass
class ShippingOption:
    carrier: str
    method: str
    cost_usd: float
    estimated_days: str
    trackable: bool = True


@dataclass
class ShippingResult:
    can_ship: bool
    validation: ShippingValidation
    options: list[ShippingOption] = field(default_factory=list)
    origin_country: str = ""
    destination_country: str = ""
    error: str = ""


@dataclass
class SupplierCategory:
    category_id: str
    name: str
    parent_id: str = ""
    parent_name: str = ""
    level: int = 3


@runtime_checkable
class SupplierAdapter(Protocol):
    """Supplier-agnostic interface. Not every method needs implementation for validation."""

    supplier_name: str

    async def authenticate(self) -> bool: ...

    async def get_categories(self) -> list[SupplierCategory]: ...

    async def search_products(
        self, keyword: str, *, category_id: str = "", page: int = 1, page_size: int = 20
    ) -> list[RawSupplierProduct]: ...

    async def get_product(self, product_id: str) -> RawSupplierProduct | None: ...

    async def get_variants(self, product_id: str) -> list[RawVariant]: ...

    async def get_inventory(self, variant_id: str) -> InventorySnapshot | None: ...

    async def calculate_shipping(
        self,
        variant_id: str,
        destination_country: str,
        *,
        origin_country: str = "CN",
        quantity: int = 1,
    ) -> ShippingResult: ...
