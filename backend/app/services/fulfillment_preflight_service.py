from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Product, ProductVariant, SupplierVariantInventory
from app.suppliers.base import ShippingOption, ShippingResult
from app.suppliers.factory import build_supplier_adapter


@dataclass(frozen=True)
class FulfillmentPreflightResult:
    status: str
    product_id: UUID
    variant_id: UUID
    supplier_variant_id: str
    destination_country: str
    requested_quantity: int
    origin_country: str | None = None
    storage_id: str | None = None
    warehouse_name: str | None = None
    sellable_inventory: int = 0
    logistics_name: str | None = None
    shipping_cost_usd: float | None = None
    delivery_estimate: str | None = None
    reason: str | None = None
    error_classification: str | None = None
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class FulfillmentPreflightService:
    def __init__(self, db: Session, adapter: Any | None = None) -> None:
        self.db = db
        self.adapter = adapter

    async def check(
        self,
        *,
        product_id: UUID,
        variant_id: UUID,
        quantity: int,
        destination_country: str,
        logistics_name: str | None = None,
        storage_id: str | None = None,
    ) -> FulfillmentPreflightResult:
        product, variant = self.db.execute(
            select(Product, ProductVariant)
            .join(ProductVariant, ProductVariant.product_id == Product.id)
            .where(Product.id == product_id, ProductVariant.id == variant_id)
        ).one_or_none() or (None, None)
        supplier_variant_id = variant.supplier_variant_id if variant else ""
        base = dict(
            product_id=product_id,
            variant_id=variant_id,
            supplier_variant_id=supplier_variant_id,
            destination_country=destination_country,
            requested_quantity=quantity,
        )
        if product is None or variant is None:
            return self._failed(**base, reason="Product or variant not found", error_classification="NOT_FOUND")
        if product.status != "ACTIVE" or not variant.active:
            return self._failed(**base, reason="Product or variant is not active", error_classification="INACTIVE")
        if quantity <= 0:
            return self._failed(**base, reason="Requested quantity must be positive", error_classification="INVALID_REQUEST")

        warehouses = list(
            self.db.scalars(
                select(SupplierVariantInventory).where(
                    SupplierVariantInventory.product_id == product_id,
                    SupplierVariantInventory.variant_id == variant_id,
                    SupplierVariantInventory.supplier_variant_id == variant.supplier_variant_id,
                )
            )
        )
        candidates = [
            warehouse
            for warehouse in warehouses
            if warehouse.cj_sellable_inventory >= quantity
            and (storage_id is None or warehouse.storage_id == storage_id)
        ]
        if not candidates:
            reason = "No warehouse has enough sellable inventory"
            if not warehouses:
                reason = "No warehouse inventory is recorded for this variant"
            return self._failed(**base, reason=reason, error_classification="INVENTORY")

        try:
            adapter = self.adapter or build_supplier_adapter(product.supplier)
        except (ValueError, RuntimeError) as exc:
            return self._failed(**base, reason=str(exc), error_classification="SUPPLIER_CONFIGURATION")
        options: list[tuple[SupplierVariantInventory, ShippingOption]] = []
        for warehouse in candidates:
            try:
                shipping = await adapter.calculate_shipping(
                    variant.supplier_variant_id,
                    destination_country,
                    origin_country=warehouse.warehouse_country,
                    quantity=quantity,
                )
            except (httpx.HTTPError, ValueError, TypeError) as exc:
                return self._failed(
                    **base,
                    reason="Supplier freight validation failed",
                    error_classification="TEMPORARY_SUPPLIER_ERROR",
                    origin_country=warehouse.warehouse_country,
                    storage_id=warehouse.storage_id,
                    warehouse_name=warehouse.warehouse_name,
                    sellable_inventory=warehouse.cj_sellable_inventory,
                )
            if shipping.error and not shipping.options and shipping.validation.value == "UNKNOWN":
                return self._failed(
                    **base,
                    reason=shipping.error,
                    error_classification="TEMPORARY_SUPPLIER_ERROR",
                    origin_country=warehouse.warehouse_country,
                    storage_id=warehouse.storage_id,
                    warehouse_name=warehouse.warehouse_name,
                    sellable_inventory=warehouse.cj_sellable_inventory,
                )
            for option in shipping.options:
                if option.carrier and (option.storage_id is None or option.storage_id == warehouse.storage_id):
                    options.append((warehouse, option))

        selected = self._select_option(options, logistics_name)
        if selected is None:
            return self._failed(
                **base,
                reason="No warehouse has both sufficient sellable inventory and a valid destination shipping route",
                error_classification="NO_LOGISTICS",
            )
        warehouse, option = selected
        return FulfillmentPreflightResult(
            **base,
            status="FULFILLABLE",
            origin_country=warehouse.warehouse_country,
            storage_id=warehouse.storage_id,
            warehouse_name=warehouse.warehouse_name,
            sellable_inventory=warehouse.cj_sellable_inventory,
            logistics_name=option.carrier,
            shipping_cost_usd=option.cost_usd,
            delivery_estimate=option.estimated_days,
        )

    @staticmethod
    def _select_option(
        options: list[tuple[SupplierVariantInventory, ShippingOption]],
        requested_name: str | None,
    ) -> tuple[SupplierVariantInventory, ShippingOption] | None:
        if requested_name:
            requested = [entry for entry in options if entry[1].carrier == requested_name]
            if requested:
                options = requested
        if not options:
            return None
        return min(options, key=lambda entry: (entry[1].cost_usd, _delivery_days(entry[1].estimated_days), entry[1].carrier, entry[0].warehouse_identity))

    @staticmethod
    def _failed(**values: Any) -> FulfillmentPreflightResult:
        values["status"] = "NOT_FULFILLABLE"
        return FulfillmentPreflightResult(**values)


def _delivery_days(value: str) -> int:
    digits = "".join(character for character in value if character.isdigit())
    return int(digits) if digits else 10**9