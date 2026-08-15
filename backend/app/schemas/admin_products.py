from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


CatalogStatus = Literal["DRAFT", "ACTIVE", "PAUSED"]


class ProductImportRequest(BaseModel):
    supplier: Literal["cj"]
    supplier_product_id: str
    destination: str = "IN"


class ProductStatusUpdate(BaseModel):
    status: CatalogStatus


class AdminProductVariantDTO(BaseModel):
    id: UUID
    supplier_variant_id: str
    supplier_variant_sku: str
    name: str
    attributes: str
    supplier_cost: Decimal | None
    total_inventory: int | None
    cj_inventory: int | None
    factory_inventory: int | None
    verified_warehouse: str | None
    weight_grams: Decimal | None
    active: bool
    position: int


class AdminProductDTO(BaseModel):
    id: UUID
    slug: str
    name: str
    description: str
    status: str
    supplier: str | None
    supplier_product_id: str | None
    supplier_source_url: str | None
    supplier_cost: Decimal | None
    shipping_cost: Decimal | None
    selling_price: Decimal | None
    currency: str
    total_inventory: int | None
    cj_inventory: int | None
    factory_inventory: int | None
    verified_warehouse: str | None
    last_supplier_sync_at: str | None
    images: list[str]
    variants: list[AdminProductVariantDTO]


class AdminProductListResponse(BaseModel):
    products: list[AdminProductDTO]
    total: int
