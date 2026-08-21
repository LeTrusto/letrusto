import asyncio
import base64
import hashlib
import hmac
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.exceptions import BadRequestError
from app.db.session import SessionLocal
from app.models.entities import InventoryReservation, Order, Product, ProductVariant, User
from app.schemas.orders import CartItemRequest, CreateOrderRequest, CustomerDetails, ShippingAddress
from app.services.cancellation_service import CancellationService
from app.services.cashfree_service import CashfreeService
from app.services.inventory_reservation_service import InventoryReservationService
from app.services.order_service import OrderService


def settings():
    return SimpleNamespace(
        CASHFREE_ENV="sandbox",
        CASHFREE_APP_ID="app",
        CASHFREE_SECRET_KEY="secret",
        CASHFREE_WEBHOOK_SECRET="webhook",
        CASHFREE_API_VERSION="2026-01-01",
        CASHFREE_RETURN_URL="http://localhost/orders/{order_id}",
        CASHFREE_NOTIFY_URL="http://localhost/webhook",
        INVENTORY_RESERVATION_TTL_MINUTES=15,
    )


def payload(slug: str, key: str, quantity: int = 1, variant_id: str = "variant-1"):
    return CreateOrderRequest(
        items=[CartItemRequest(product_id=slug, variant_id=variant_id, quantity=quantity)],
        customer=CustomerDetails(name="Reservation Buyer", email="reservation@example.com", phone="9876543210"),
        shipping_address=ShippingAddress(address="1 Test Street", city="Bengaluru", state="Karnataka", postal_code="560001", country="IN"),
        idempotency_key=key,
    )


def fixture(db, *, inventory=5, factory_inventory=999, variant_count=1):
    suffix = uuid4().hex[:8]
    user = User(email=f"reservation-{suffix}@example.com", full_name="Reservation Buyer")
    other = User(email=f"reservation-other-{suffix}@example.com", full_name="Other Buyer")
    product = Product(
        slug=f"reservation-product-{suffix}", name="Reservation Product", description="test", status="ACTIVE",
        supplier="cj", supplier_product_id=f"CJ-{suffix}", price_value=Decimal("100"), selling_price=Decimal("100"),
        ai_score=1, rating=Decimal("1"), ai_summary="", review_summary="",
    )
    variants = [
        ProductVariant(
            product=product, supplier_variant_id=f"VID-{suffix}-{index}", supplier_variant_sku=f"SKU-{suffix}-{index}",
            name=f"Variant {index}", position=index, selling_price=Decimal("100"), cj_inventory=inventory if index == 1 else 2,
            factory_inventory=factory_inventory, active=True,
        )
        for index in range(1, variant_count + 1)
    ]
    db.add_all([user, other, product, *variants])
    db.commit()
    return user, other, product, variants


def cleanup(db, user, other, product):
    db.query(InventoryReservation).filter(InventoryReservation.order_id.in_(db.query(Order.id).filter(Order.user_id.in_([user.id, other.id])))).delete(synchronize_session=False)
    db.query(Order).filter(Order.user_id.in_([user.id, other.id])).delete(synchronize_session=False)
    db.delete(user)
    db.delete(other)
    db.delete(product)
    db.commit()
    db.close()


def test_order_creation_creates_active_reservation_from_cj_only():
    db = SessionLocal()
    user, other, product, variants = fixture(db, inventory=3, factory_inventory=999)
    try:
        result = OrderService(db).create_order(user, payload(product.slug, "reservation-active" , quantity=2))
        reservation = db.query(InventoryReservation).filter(InventoryReservation.order_id == result.id).one()
        assert reservation.status == "ACTIVE"
        assert reservation.quantity == 2
        assert reservation.variant_id == variants[0].id
        assert reservation.expires_at > datetime.now(timezone.utc)
    finally:
        cleanup(db, user, other, product)


def test_active_reservations_reduce_available_cj_inventory():
    db = SessionLocal()
    user, other, product, _ = fixture(db, inventory=2)
    try:
        OrderService(db).create_order(user, payload(product.slug, "reservation-first", quantity=2))
        with pytest.raises(BadRequestError, match="currently available"):
            OrderService(db).create_order(other, payload(product.slug, "reservation-second", quantity=1))
    finally:
        cleanup(db, user, other, product)


def test_factory_inventory_never_increases_availability():
    db = SessionLocal()
    user, other, product, _ = fixture(db, inventory=0, factory_inventory=999)
    try:
        reservations_before = db.query(InventoryReservation).count()
        with pytest.raises(BadRequestError, match="out of stock"):
            OrderService(db).create_order(user, payload(product.slug, "factory-only"))
        assert db.query(InventoryReservation).count() == reservations_before
    finally:
        cleanup(db, user, other, product)


def test_duplicate_order_submission_creates_one_reservation():
    db = SessionLocal()
    user, other, product, _ = fixture(db, inventory=3)
    try:
        first = OrderService(db).create_order(user, payload(product.slug, "duplicate-key"))
        second = OrderService(db).create_order(user, payload(product.slug, "duplicate-key"))
        assert first.id == second.id
        assert db.query(InventoryReservation).filter(InventoryReservation.order_id == first.id).count() == 1
    finally:
        cleanup(db, user, other, product)


def test_mixed_variants_reserve_each_order_item():
    db = SessionLocal()
    user, other, product, variants = fixture(db, inventory=3, variant_count=2)
    try:
        request = CreateOrderRequest(
            items=[
                CartItemRequest(product_id=product.slug, variant_id="variant-1", quantity=2),
                CartItemRequest(product_id=product.slug, variant_id="variant-2", quantity=1),
            ],
            customer=CustomerDetails(name="Reservation Buyer", email="mixed@example.com", phone="9876543210"),
            shipping_address=ShippingAddress(address="1 Test Street", city="Bengaluru", state="Karnataka", postal_code="560001", country="IN"),
            idempotency_key="mixed-variants",
        )
        result = OrderService(db).create_order(user, request)
        reservations = db.query(InventoryReservation).filter(InventoryReservation.order_id == result.id).all()
        assert sorted(row.quantity for row in reservations) == [1, 2]
        assert len({row.order_item_id for row in reservations}) == 2
    finally:
        cleanup(db, user, other, product)


def test_payment_success_consumes_reservation_without_local_inventory_decrement(monkeypatch):
    db = SessionLocal()
    user, other, product, variants = fixture(db, inventory=3)
    try:
        result = OrderService(db).create_order(user, payload(product.slug, "payment-success"))
        order = db.get(Order, result.id)
        order.provider_order_id = f"cf-{uuid4().hex}"
        db.commit()
        async def no_fulfillment(_, __):
            return order
        monkeypatch.setattr("app.services.cashfree_service.FulfillmentService.submit", no_fulfillment)
        body = json.dumps({"data": {"order": {"order_id": order.provider_order_id}, "payment": {"payment_status": "SUCCESS", "cf_payment_id": "pay-1"}}}).encode()
        timestamp = "payment-success-test"
        signature = base64.b64encode(hmac.new(b"webhook", timestamp.encode() + body, hashlib.sha256).digest()).decode()
        asyncio.run(CashfreeService(db, settings()).process_webhook(body, timestamp, signature))
        db.refresh(order)
        reservation = db.query(InventoryReservation).filter(InventoryReservation.order_id == order.id).one()
        assert reservation.status == "CONSUMED"
        assert order.payment_status == "PAID"
        assert variants[0].cj_inventory == 3
    finally:
        cleanup(db, user, other, product)


def test_payment_failure_releases_reservation():
    db = SessionLocal()
    user, other, product, _ = fixture(db, inventory=3)
    try:
        result = OrderService(db).create_order(user, payload(product.slug, "payment-failure"))
        order = db.get(Order, result.id)
        order.provider_order_id = f"cf-{uuid4().hex}"
        db.commit()
        body = json.dumps({"data": {"order": {"order_id": order.provider_order_id}, "payment": {"payment_status": "FAILED", "payment_message": "declined", "cf_payment_id": "pay-2"}}}).encode()
        timestamp = "payment-failure-test"
        signature = base64.b64encode(hmac.new(b"webhook", timestamp.encode() + body, hashlib.sha256).digest()).decode()
        asyncio.run(CashfreeService(db, settings()).process_webhook(body, timestamp, signature))
        reservation = db.query(InventoryReservation).filter(InventoryReservation.order_id == order.id).one()
        assert reservation.status == "RELEASED"
        assert order.payment_status == "FAILED"
    finally:
        cleanup(db, user, other, product)


def test_unpaid_cancellation_releases_reservation():
    db = SessionLocal()
    user, other, product, _ = fixture(db, inventory=3)
    try:
        result = OrderService(db).create_order(user, payload(product.slug, "cancel-release"))
        order = db.get(Order, result.id)
        CancellationService(db).cancel_by_customer(user, order.id)
        reservation = db.query(InventoryReservation).filter(InventoryReservation.order_id == order.id).one()
        assert reservation.status == "RELEASED"
    finally:
        cleanup(db, user, other, product)


def test_expired_reservation_is_released_and_no_longer_counts():
    db = SessionLocal()
    user, other, product, variants = fixture(db, inventory=3)
    try:
        result = OrderService(db).create_order(user, payload(product.slug, "expiration"))
        reservation = db.query(InventoryReservation).filter(InventoryReservation.order_id == result.id).one()
        reservation.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.commit()
        assert InventoryReservationService(db).release_expired() == 1
        db.refresh(reservation)
        assert reservation.status == "EXPIRED"
        assert InventoryReservationService(db).active_quantity(variants[0].id) == 0
    finally:
        cleanup(db, user, other, product)


def test_two_concurrent_checkouts_cannot_reserve_final_unit():
    db = SessionLocal()
    user, other, product, _ = fixture(db, inventory=1)
    user_id = user.id
    other_id = other.id
    product_slug = product.slug
    barrier = __import__("threading").Barrier(2)

    def attempt(user_id):
        session = SessionLocal()
        try:
            customer = session.get(User, user_id)
            barrier.wait(timeout=5)
            OrderService(session).create_order(customer, payload(product_slug, f"concurrent-{user_id}"))
            return "success"
        except BadRequestError:
            return "unavailable"
        finally:
            session.close()

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(attempt, [user_id, other_id]))
        assert sorted(results) == ["success", "unavailable"]
        check = SessionLocal()
        assert check.query(InventoryReservation).filter(InventoryReservation.order_id.in_(check.query(Order.id).filter(Order.user_id.in_([user_id, other_id]))), InventoryReservation.status == "ACTIVE").count() == 1
        check.close()
    finally:
        cleanup(db, user, other, product)
