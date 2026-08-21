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


class SupplierOrderState(str, Enum):
    CREATED = "CREATED"
    IN_CART = "IN_CART"
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    PAID = "PAID"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class SupplierPaymentState(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    REQUIRED = "REQUIRED"
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


@dataclass
class InventorySnapshot:
    total_inventory: int
    cj_inventory: int
    factory_inventory: int
    verification_status: str | None = None
    warehouses: list["WarehouseInventorySnapshot"] = field(default_factory=list)


@dataclass
class WarehouseInventorySnapshot:
    warehouse_country: str
    storage_id: str | None
    warehouse_name: str | None
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
    warehouses: list[WarehouseInventorySnapshot] = field(default_factory=list)


@dataclass
class ShippingOption:
    carrier: str
    method: str
    cost_usd: float
    estimated_days: str
    trackable: bool = True
    storage_id: str | None = None
    provider_metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class ShippingResult:
    can_ship: bool
    validation: ShippingValidation
    options: list[ShippingOption] = field(default_factory=list)
    origin_country: str = ""
    destination_country: str = ""
    error: str = ""
    error_details: object | None = None


@dataclass
class SupplierOrderResult:
    accepted: bool
    supplier_order_id: str | None = None
    status: str = "FAILED"
    supplier_status: str | None = None
    pay_id: str | None = None
    payment_url: str | None = None
    shipment_order_id: str | None = None
    created_at: str | None = None
    provider_metadata: dict[str, object] = field(default_factory=dict)
    payment_state: str | None = None
    error: str = ""
    error_details: object | None = None


@dataclass
class SupplierBalanceResult:
    supported: bool
    amount_usd: float | None = None
    no_withdrawal_amount_usd: float | None = None
    freeze_amount_usd: float | None = None
    error: str = ""
    error_details: object | None = None


@dataclass
class SupplierTrackingResult:
    supported: bool
    supplier_status: str | None = None
    tracking_number: str | None = None
    carrier: str | None = None
    shipped_at: str | None = None
    delivered_at: str | None = None
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

    async def get_product(self, product_id: str, *, strict: bool = False) -> RawSupplierProduct | None: ...

    async def get_variants(self, product_id: str) -> list[RawVariant]: ...

    async def get_inventory(self, variant_id: str, *, strict: bool = False) -> InventorySnapshot | None: ...

    async def calculate_shipping(
        self,
        variant_id: str,
        destination_country: str,
        *,
        origin_country: str = "CN",
        quantity: int = 1,
    ) -> ShippingResult: ...

    async def create_order(self, payload: dict) -> SupplierOrderResult: ...

    async def add_to_cart(self, supplier_order_id: str) -> SupplierOrderResult: ...

    async def confirm_order(self, supplier_order_id: str) -> SupplierOrderResult: ...

    async def generate_parent_order(self, supplier_order_id: str) -> SupplierOrderResult: ...

    async def pay_balance(self, shipment_order_id: str, pay_id: str | None = None) -> SupplierOrderResult: ...

    async def get_balance(self) -> SupplierBalanceResult: ...

    async def get_order_status(self, supplier_order_id: str) -> SupplierOrderResult: ...

    async def cancel_order(self, supplier_order_id: str) -> SupplierOrderResult: ...

    async def get_tracking(self, supplier_order_id: str) -> SupplierTrackingResult: ...
