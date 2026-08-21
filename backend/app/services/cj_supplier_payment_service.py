"""Explicit, non-Razorpay CJ supplier payment orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

from app.suppliers.base import SupplierAdapter, SupplierBalanceResult, SupplierOrderResult, SupplierPaymentState


@dataclass
class SupplierPaymentRecord:
    supplier_order_id: str | None
    shipment_order_id: str | None
    payment_state: str = SupplierPaymentState.REQUIRED.value
    supplier_status: str | None = None
    pay_id: str | None = None
    payment_error: str | None = None
    payment_attempted_at: datetime | None = None
    payment_confirmed_at: datetime | None = None


class CJSupplierPaymentService:
    """Manage CJ balance payment without connecting to customer payment flow."""

    def __init__(self, adapter: SupplierAdapter) -> None:
        self.adapter = adapter

    async def check_balance(self, required_amount_usd: float) -> SupplierBalanceResult:
        result = await self.adapter.get_balance()
        if not result.supported or result.amount_usd is None:
            return result
        available = result.amount_usd - (result.freeze_amount_usd or 0.0)
        if available < required_amount_usd:
            result.error = "CJ balance is insufficient"
            result.error_details = {"code": "INSUFFICIENT_BALANCE", "available_usd": available, "required_usd": required_amount_usd}
        return result

    async def reconcile(self, record: SupplierPaymentRecord) -> SupplierOrderResult:
        if not record.supplier_order_id:
            result = SupplierOrderResult(accepted=False, status="FAILED", payment_state=SupplierPaymentState.FAILED.value, error="Supplier order ID is missing")
            self._apply(record, result)
            return result
        result = await self.adapter.get_order_status(record.supplier_order_id)
        if not result.accepted:
            result.payment_state = SupplierPaymentState.FAILED.value
            self._apply(record, result)
            return result
        if _is_supplier_paid(result):
            result.payment_state = SupplierPaymentState.PAID.value
            record.payment_confirmed_at = datetime.now(timezone.utc)
        else:
            result.payment_state = SupplierPaymentState.REQUIRED.value
        self._apply(record, result)
        return result

    async def pay(self, record: SupplierPaymentRecord, *, required_amount_usd: float) -> SupplierOrderResult:
        if not record.supplier_order_id or not record.shipment_order_id:
            result = SupplierOrderResult(accepted=False, status="FAILED", payment_state=SupplierPaymentState.FAILED.value, error="CJ payment requires a supplier order and shipment order")
            self._apply(record, result)
            return result
        if record.payment_state == SupplierPaymentState.PAID.value:
            return SupplierOrderResult(accepted=True, supplier_order_id=record.supplier_order_id, status="PAID", supplier_status=record.supplier_status, payment_state=SupplierPaymentState.PAID.value)
        if record.payment_state in {SupplierPaymentState.PENDING.value, SupplierPaymentState.UNKNOWN.value}:
            return await self.reconcile(record)

        current = await self.reconcile(record)
        if current.payment_state == SupplierPaymentState.PAID.value:
            return current
        if current.supplier_status != "UNPAID":
            current.payment_state = SupplierPaymentState.FAILED.value
            current.error = "CJ order is not explicitly UNPAID; payment was blocked"
            self._apply(record, current)
            return current

        balance = await self.check_balance(required_amount_usd)
        if balance.error:
            result = SupplierOrderResult(accepted=False, supplier_order_id=record.supplier_order_id, status="FAILED", supplier_status="UNPAID", payment_state=SupplierPaymentState.FAILED.value, error=balance.error, error_details=balance.error_details)
            self._apply(record, result)
            return result

        record.payment_state = SupplierPaymentState.PENDING.value
        record.payment_attempted_at = datetime.now(timezone.utc)
        try:
            result = await self.adapter.pay_balance(record.shipment_order_id, record.pay_id)
        except (httpx.TimeoutException, TimeoutError) as exc:
            result = SupplierOrderResult(accepted=False, supplier_order_id=record.supplier_order_id, status="UNKNOWN", supplier_status="UNPAID", payment_state=SupplierPaymentState.UNKNOWN.value, error=f"CJ payment request timed out: {exc}")
            self._apply(record, result)
            return result
        self._apply(record, result)
        if not result.accepted:
            result.payment_state = SupplierPaymentState.FAILED.value
            self._apply(record, result)
            return result
        result.payment_state = SupplierPaymentState.PENDING.value
        self._apply(record, result)
        return result

    @staticmethod
    def _apply(record: SupplierPaymentRecord, result: SupplierOrderResult) -> None:
        if result.supplier_status:
            record.supplier_status = result.supplier_status
        if result.pay_id:
            record.pay_id = result.pay_id
        if result.payment_state:
            record.payment_state = result.payment_state
        if result.error:
            record.payment_error = result.error[:500]


def _is_supplier_paid(result: SupplierOrderResult) -> bool:
    return result.status in {"PAID", "PROCESSING", "SHIPPED", "DELIVERED"} or result.supplier_status in {"UNSHIPPED", "SHIPPED", "DELIVERED"}


def apply_payment_record_to_order(order: Any, record: SupplierPaymentRecord) -> None:
    """Copy the payment state into an Order-like model without committing it."""
    order.supplier_payment_state = record.payment_state
    order.supplier_pay_id = record.pay_id
    order.supplier_payment_attempted_at = record.payment_attempted_at
    order.supplier_payment_confirmed_at = record.payment_confirmed_at
    order.supplier_payment_error = record.payment_error
    order.supplier_payment_updated_at = datetime.now(timezone.utc)