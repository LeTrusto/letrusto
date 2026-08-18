import base64
import asyncio
import hashlib
import hmac
import json
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest

from app.core.exceptions import BadRequestError
from app.db.session import SessionLocal
from app.models.entities import Cart, CartItem, Order, OrderItem, PaymentAttempt, Product, ProductVariant, User
from app.services.cashfree_service import CashfreeService
from app.services.order_service import OrderService
from app.schemas.orders import CartItemRequest, CreateOrderRequest, CustomerDetails, ShippingAddress


def make_order(db):
    suffix = uuid4().hex[:8]
    user = User(email=f"cashfree-{suffix}@example.com", full_name="Cashfree Test")
    product = Product(slug=f"cashfree-product-{suffix}", name="Cashfree product", description="test", status="ACTIVE", supplier="cj", supplier_product_id=f"cashfree-cj-{suffix}", price_value=Decimal("100"), selling_price=Decimal("100"), ai_score=1, rating=Decimal("1"), ai_summary="", review_summary="")
    variant = ProductVariant(product=product, supplier_variant_id=f"VID-{suffix}", supplier_variant_sku=f"SKU-{suffix}", name="Blue", position=1, selling_price=Decimal("100"), cj_inventory=2, factory_inventory=999)
    db.add_all([user, product]); db.commit()
    payload = CreateOrderRequest(items=[CartItemRequest(product_id=product.slug, variant_id="variant-1", quantity=1)], customer=CustomerDetails(name="Buyer", email="buyer@example.com", phone="9876543210"), shipping_address=ShippingAddress(address="1 Street", city="Bengaluru", state="Karnataka", postal_code="560001", country="IN"), idempotency_key=f"cashfree-{suffix}-key")
    order = OrderService(db).create_order(user, payload)
    return user, product, db.get(Order, order.id)


def settings(**overrides):
    values = dict(CASHFREE_ENV="sandbox", CASHFREE_APP_ID="app", CASHFREE_SECRET_KEY="secret", CASHFREE_WEBHOOK_SECRET="webhook", CASHFREE_API_VERSION="2026-01-01", CASHFREE_RETURN_URL="http://localhost/orders/{order_id}", CASHFREE_NOTIFY_URL="http://localhost/webhook")
    values.update(overrides)
    return SimpleNamespace(**values)


def cleanup(db, user, product):
    order_ids = [row[0] for row in db.query(Order.id).filter(Order.user_id == user.id).all()]
    if order_ids:
        db.query(PaymentAttempt).filter(PaymentAttempt.order_id.in_(order_ids)).delete(synchronize_session=False)
        db.query(OrderItem).filter(OrderItem.order_id.in_(order_ids)).delete(synchronize_session=False)
        db.query(Order).filter(Order.id.in_(order_ids)).delete(synchronize_session=False)
    cart = db.query(Cart).filter(Cart.user_id == user.id).one_or_none()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete(synchronize_session=False)
        db.delete(cart)
    db.delete(product); db.delete(user); db.commit(); db.close()


def test_missing_credentials_fail_closed():
    db = SessionLocal(); user, product, order = make_order(db)
    try:
        with pytest.raises(BadRequestError, match="credentials"):
            CashfreeService(db, settings(CASHFREE_APP_ID="", CASHFREE_SECRET_KEY="")).create_session(user, order.id)
    finally: cleanup(db, user, product)


def test_session_uses_authoritative_order_total_and_hides_secret(monkeypatch):
    db = SessionLocal(); user, product, order = make_order(db); calls = []
    def fake_post(url, **kwargs):
        calls.append((url, kwargs)); return httpx.Response(200, json={"order_id": order.order_number, "payment_session_id": "session-safe"})
    monkeypatch.setattr(httpx, "post", fake_post)
    try:
        result = CashfreeService(db, settings()).create_session(user, order.id)
        assert result.payment_session_id == "session-safe"
        assert result.amount == Decimal("100.00")
        assert "secret" not in result.model_dump_json()
        assert calls[0][1]["json"]["order_amount"] == 100.0
        assert calls[0][1]["headers"]["x-client-secret"] == "secret"
        db.refresh(order); assert order.payment_provider == "CASHFREE"
    finally: cleanup(db, user, product)


def test_failed_order_retry_uses_new_provider_order_id(monkeypatch):
    db = SessionLocal(); user, product, order = make_order(db); calls = []
    def fake_post(url, **kwargs):
        calls.append(kwargs["json"]["order_id"])
        return httpx.Response(200, json={"order_id": calls[-1], "payment_session_id": f"session-{len(calls)}"})
    monkeypatch.setattr(httpx, "post", fake_post)
    try:
        service = CashfreeService(db, settings())
        first = service.create_session(user, order.id)
        db.refresh(order); order.payment_status = "FAILED"; db.commit()
        second = service.create_session(user, order.id)
        assert first.provider_order_id != second.provider_order_id
        assert len(calls) == 2
    finally: cleanup(db, user, product)


def test_webhook_signature_and_duplicate_success_are_idempotent():
    db = SessionLocal(); user, product, order = make_order(db); service = CashfreeService(db, settings())
    order.payment_provider = "CASHFREE"
    order.provider_order_id = order.order_number
    db.commit()
    body = json.dumps({"data": {"order": {"order_id": order.order_number}, "payment": {"cf_payment_id": "cf-pay-1", "payment_status": "SUCCESS"}}}).encode()
    timestamp = "1700000000000"
    signature = base64.b64encode(hmac.new(b"webhook", timestamp.encode() + body, hashlib.sha256).digest()).decode()
    try:
        asyncio.run(service.process_webhook(body, timestamp, signature)); asyncio.run(service.process_webhook(body, timestamp, signature))
        db.refresh(order)
        assert order.payment_status == "PAID"; assert order.status == "PAID"; assert order.fulfillment_status == "FAILED"
        with pytest.raises(BadRequestError, match="signature"):
            asyncio.run(service.process_webhook(body, timestamp, "bad"))
    finally: cleanup(db, user, product)
