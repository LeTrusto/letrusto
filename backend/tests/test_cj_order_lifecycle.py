import asyncio
import base64
import hashlib
import hmac
import json

from app.services.cj_order_lifecycle_service import CJSupplierOrderLifecycleService, SupplierLifecycleRecord
from app.suppliers.base import SupplierOrderResult
from app.suppliers.cj_webhooks import CJWebhookDeduplicator, parse_cj_webhook


class FakeCJAdapter:
    def __init__(self):
        self.create_calls = 0
        self.pay_calls = 0

    async def create_order(self, payload):
        self.create_calls += 1
        return SupplierOrderResult(accepted=True, supplier_order_id="cj-1", status="CREATED")

    async def add_to_cart(self, supplier_order_id):
        return SupplierOrderResult(accepted=True, supplier_order_id=supplier_order_id, status="IN_CART")

    async def confirm_order(self, supplier_order_id):
        return SupplierOrderResult(accepted=True, supplier_order_id=supplier_order_id, status="IN_CART")

    async def generate_parent_order(self, supplier_order_id):
        return SupplierOrderResult(accepted=True, supplier_order_id=supplier_order_id, status="AWAITING_PAYMENT", pay_id="pay-1")

    async def pay_balance(self, shipment_order_id, pay_id=None):
        self.pay_calls += 1
        return SupplierOrderResult(accepted=True, supplier_order_id=shipment_order_id, status="PAID")

    async def get_order_status(self, supplier_order_id):
        return SupplierOrderResult(accepted=True, supplier_order_id=supplier_order_id, status="PROCESSING")

    async def cancel_order(self, supplier_order_id):
        return SupplierOrderResult(accepted=True, supplier_order_id=supplier_order_id, status="CANCELLED")


def test_create_is_idempotent_and_does_not_pay():
    adapter = FakeCJAdapter()
    service = CJSupplierOrderLifecycleService(adapter)
    payload = {"orderNumber": "LT-100", "products": []}

    first = asyncio.run(service.create(payload))
    repeated = asyncio.run(service.create(payload, existing=SupplierLifecycleRecord("LT-100", "cj-1", "CREATED")))

    assert first.supplier_order_id == repeated.supplier_order_id == "cj-1"
    assert adapter.create_calls == 1
    assert adapter.pay_calls == 0


def test_payment_is_explicit_and_parent_order_requires_payment():
    adapter = FakeCJAdapter()
    service = CJSupplierOrderLifecycleService(adapter)

    prepared = asyncio.run(service.prepare_payment("cj-1"))
    assert prepared.status == "AWAITING_PAYMENT"
    assert prepared.pay_id == "pay-1"
    assert adapter.pay_calls == 0

    paid = asyncio.run(service.pay("cj-1", prepared.pay_id))
    assert paid.status == "PAID"
    assert adapter.pay_calls == 1


def test_cancel_only_supports_created_and_in_cart():
    adapter = FakeCJAdapter()
    service = CJSupplierOrderLifecycleService(adapter)

    blocked = asyncio.run(service.cancel(SupplierLifecycleRecord("LT-100", "cj-1", "PAID")))
    cancelled = asyncio.run(service.cancel(SupplierLifecycleRecord("LT-101", "cj-2", "IN_CART")))

    assert blocked.accepted is False
    assert blocked.status == "UNSUPPORTED"
    assert cancelled.status == "CANCELLED"


def test_webhook_uses_raw_body_signature_and_deduplicates_message_id():
    open_id = "open-id"
    raw_body = json.dumps({"messageId": "m-1", "type": "ORDER", "messageType": "STATUS", "params": {"orderId": "cj-1"}}).encode()
    signature = base64.b64encode(hmac.new(open_id.encode(), raw_body, hashlib.sha256).digest()).decode()

    event = parse_cj_webhook(raw_body, open_id=open_id, signature=signature)
    deduplicator = CJWebhookDeduplicator()
    assert deduplicator.accept(event) is True
    assert deduplicator.accept(event) is False