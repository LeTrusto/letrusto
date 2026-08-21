import asyncio

import httpx

from app.services.cj_supplier_payment_service import CJSupplierPaymentService, SupplierPaymentRecord
from app.suppliers.base import SupplierBalanceResult, SupplierOrderResult


class FakePaymentAdapter:
    def __init__(self, *, status="UNPAID", balance=100.0, pay_result=None, pay_error=None):
        self.status = status
        self.balance = balance
        self.pay_result = pay_result or SupplierOrderResult(accepted=True, supplier_order_id="CJ-1", status="AWAITING_PAYMENT", supplier_status="UNPAID", payment_state="PENDING")
        self.pay_error = pay_error
        self.pay_calls = 0

    async def get_order_status(self, supplier_order_id):
        if supplier_order_id != "CJ-1":
            return SupplierOrderResult(accepted=False, error="order not found")
        return SupplierOrderResult(accepted=True, supplier_order_id="CJ-1", status="PAID" if self.status == "PAID" else "AWAITING_PAYMENT", supplier_status=self.status)

    async def get_balance(self):
        return SupplierBalanceResult(supported=True, amount_usd=self.balance, freeze_amount_usd=0)

    async def pay_balance(self, shipment_order_id, pay_id=None):
        self.pay_calls += 1
        if self.pay_error:
            raise self.pay_error
        return self.pay_result


def record(state="REQUIRED"):
    return SupplierPaymentRecord("CJ-1", "SHIP-1", payment_state=state)


def test_unpaid_with_sufficient_balance_is_allowed_but_pending():
    adapter = FakePaymentAdapter()
    result = asyncio.run(CJSupplierPaymentService(adapter).pay(record(), required_amount_usd=25))
    assert result.payment_state == "PENDING"
    assert adapter.pay_calls == 1


def test_paid_order_skips_duplicate_payment():
    adapter = FakePaymentAdapter(status="PAID")
    result = asyncio.run(CJSupplierPaymentService(adapter).pay(record(), required_amount_usd=25))
    assert result.payment_state == "PAID"
    assert adapter.pay_calls == 0


def test_missing_order_is_blocked():
    adapter = FakePaymentAdapter()
    result = asyncio.run(CJSupplierPaymentService(adapter).pay(SupplierPaymentRecord(None, None), required_amount_usd=25))
    assert result.payment_state == "FAILED"
    assert adapter.pay_calls == 0


def test_insufficient_balance_blocks_payment():
    adapter = FakePaymentAdapter(balance=10)
    result = asyncio.run(CJSupplierPaymentService(adapter).pay(record(), required_amount_usd=25))
    assert result.payment_state == "FAILED"
    assert result.error == "CJ balance is insufficient"
    assert result.error_details["code"] == "INSUFFICIENT_BALANCE"
    assert adapter.pay_calls == 0


def test_payment_api_failure_is_failed():
    adapter = FakePaymentAdapter(pay_result=SupplierOrderResult(accepted=False, error="CJ payment rejected"))
    result = asyncio.run(CJSupplierPaymentService(adapter).pay(record(), required_amount_usd=25))
    assert result.payment_state == "FAILED"
    assert adapter.pay_calls == 1


def test_payment_timeout_becomes_unknown_without_retry():
    adapter = FakePaymentAdapter(pay_error=httpx.ReadTimeout("timed out"))
    result = asyncio.run(CJSupplierPaymentService(adapter).pay(record(), required_amount_usd=25))
    assert result.payment_state == "UNKNOWN"
    assert adapter.pay_calls == 1


def test_response_lost_is_reconciled_from_cj_status():
    adapter = FakePaymentAdapter(status="PAID", pay_error=httpx.ReadTimeout("response lost"))
    payment = record()
    payment.payment_state = "UNKNOWN"
    result = asyncio.run(CJSupplierPaymentService(adapter).pay(payment, required_amount_usd=25))
    assert result.payment_state == "PAID"
    assert adapter.pay_calls == 0


def test_duplicate_pending_request_reconciles_without_repayment():
    adapter = FakePaymentAdapter(status="UNPAID")
    result = asyncio.run(CJSupplierPaymentService(adapter).pay(record("PENDING"), required_amount_usd=25))
    assert result.payment_state == "REQUIRED"
    assert adapter.pay_calls == 0