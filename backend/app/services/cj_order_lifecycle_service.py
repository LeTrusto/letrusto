"""Supplier-side CJ order lifecycle orchestration.

This service intentionally does not call supplier payment during creation.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from app.suppliers.base import SupplierAdapter, SupplierOrderResult


@dataclass(frozen=True)
class SupplierLifecycleRecord:
    order_number: str
    supplier_order_id: str | None = None
    state: str = "UNKNOWN"
    supplier_status: str | None = None
    pay_id: str | None = None
    payment_url: str | None = None
    shipment_order_id: str | None = None


class CJSupplierOrderLifecycleService:
    """Coordinates CJ lifecycle calls without coupling them to customer payment."""

    _locks: dict[str, asyncio.Lock] = {}

    def __init__(self, adapter: SupplierAdapter) -> None:
        self.adapter = adapter

    async def create(
        self,
        payload: dict,
        *,
        existing: SupplierLifecycleRecord | None = None,
    ) -> SupplierOrderResult:
        if existing and existing.supplier_order_id:
            return SupplierOrderResult(
                accepted=True,
                supplier_order_id=existing.supplier_order_id,
                status=existing.state,
                supplier_status=existing.supplier_status,
                pay_id=existing.pay_id,
                payment_url=existing.payment_url,
                shipment_order_id=existing.shipment_order_id,
            )
        order_number = str(payload.get("orderNumber") or "").strip()
        if not order_number:
            raise ValueError("CJ lifecycle requires orderNumber")
        lock = self._locks.setdefault(order_number, asyncio.Lock())
        async with lock:
            return await self.adapter.create_order(payload)

    async def add_to_cart(self, supplier_order_id: str) -> SupplierOrderResult:
        return await self.adapter.add_to_cart(supplier_order_id)

    async def confirm(self, supplier_order_id: str) -> SupplierOrderResult:
        return await self.adapter.confirm_order(supplier_order_id)

    async def prepare_payment(self, supplier_order_id: str) -> SupplierOrderResult:
        """Create CJ's parent/payment record and return PAYMENT_REQUIRED details."""
        return await self.adapter.generate_parent_order(supplier_order_id)

    async def pay(self, shipment_order_id: str, pay_id: str | None = None) -> SupplierOrderResult:
        """Explicit payment capability; never called implicitly by create/prepare."""
        return await self.adapter.pay_balance(shipment_order_id, pay_id)

    async def refresh(self, supplier_order_id: str) -> SupplierOrderResult:
        return await self.adapter.get_order_status(supplier_order_id)

    async def cancel(self, record: SupplierLifecycleRecord) -> SupplierOrderResult:
        if record.state not in {"CREATED", "IN_CART"}:
            return SupplierOrderResult(
                accepted=False,
                supplier_order_id=record.supplier_order_id,
                status="UNSUPPORTED",
                error="CJ cancellation is only supported for CREATED or IN_CART orders",
                error_details={"operation": "cancel", "state": record.state, "supported": False},
            )
        if not record.supplier_order_id:
            return SupplierOrderResult(accepted=False, status="UNSUPPORTED", error="Supplier order ID is missing")
        return await self.adapter.cancel_order(record.supplier_order_id)