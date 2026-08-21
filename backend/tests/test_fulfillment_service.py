from decimal import Decimal
import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.exceptions import BadRequestError
from app.db.session import SessionLocal
from app.models.entities import Cart, CartItem, Order, OrderItem, PaymentAttempt, Product, ProductVariant, User
from app.services.fulfillment_service import FulfillmentService
from app.services.inventory_reservation_service import InventoryReservationService
from app.suppliers.base import SupplierOrderResult, SupplierTrackingResult
from app.schemas.orders import CartItemRequest, CreateOrderRequest, CustomerDetails, ShippingAddress
from app.services.order_service import OrderService


class FakeCJ:
    calls = []

    async def create_order(self, payload):
        self.calls.append(payload)
        return SupplierOrderResult(
            accepted=True,
            supplier_order_id=f"CJ-ORDER-{payload['products'][0]['pid']}",
            status="SUBMITTED",
        )

    async def get_tracking(self, supplier_order_id):
        return SupplierTrackingResult(supported=True, supplier_status="shipped", tracking_number="TRACK-1", carrier="Test Carrier", shipped_at="2026-08-18T10:00:00Z")


def make_paid_order(db):
    suffix = uuid4().hex[:8]
    user = User(email=f"fulfillment-{suffix}@example.com", full_name="Fulfillment Test")
    product = Product(slug=f"fulfillment-product-{suffix}", name="Fulfillment product", description="test", status="ACTIVE", supplier="cj", supplier_product_id=f"CJ-PID-{suffix}", price_value=Decimal("100"), selling_price=Decimal("100"), ai_score=1, rating=Decimal("1"), ai_summary="", review_summary="")
    variant = ProductVariant(product=product, supplier_variant_id=f"CJ-VID-{suffix}", supplier_variant_sku=f"CJ-SKU-{suffix}", name="Blue", attributes="Blue", position=1, selling_price=Decimal("100"), cj_inventory=2, factory_inventory=999)
    db.add_all([user, product]); db.commit()
    payload = CreateOrderRequest(items=[CartItemRequest(product_id=product.slug, variant_id="variant-1", quantity=1)], customer=CustomerDetails(name="Buyer", email="buyer@example.com", phone="9876543210"), shipping_address=ShippingAddress(address="1 Street", city="Bengaluru", state="Karnataka", postal_code="560001", country="IN"), idempotency_key=f"fulfillment-{suffix}-key")
    result = OrderService(db).create_order(user, payload)
    order = db.get(Order, result.id)
    order.payment_status = "PAID"
    order.status = "PAID"
    InventoryReservationService(db).consume_for_order(order.id)
    db.commit()
    return user, product, order


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


def test_unpaid_order_is_blocked_before_cj(monkeypatch):
    db = SessionLocal(); user, product, order = make_paid_order(db); order.payment_status = "PENDING"; db.commit();
    try:
        with pytest.raises(BadRequestError, match="not eligible"):
            asyncio.run(FulfillmentService(db).submit(order.id))
    finally: cleanup(db, user, product)


def test_paid_order_maps_stored_cj_ids_and_is_idempotent(monkeypatch):
    db = SessionLocal(); user, product, order = make_paid_order(db); fake = FakeCJ(); fake.calls = []
    monkeypatch.setattr("app.services.fulfillment_service.build_supplier_adapter", lambda _: fake)
    monkeypatch.setattr("app.services.fulfillment_service.get_settings", lambda: SimpleNamespace(CJ_API_KEY="configured"))
    try:
        service = FulfillmentService(db)
        first = asyncio.run(service.submit(order.id))
        second = asyncio.run(service.submit(order.id))
        assert first.supplier_order_id == f"CJ-ORDER-{product.supplier_product_id}"
        assert second.supplier_order_id == f"CJ-ORDER-{product.supplier_product_id}"
        assert len(fake.calls) == 1
        assert fake.calls[0]["products"][0]["pid"] == product.supplier_product_id
        assert fake.calls[0]["products"][0]["vid"] == product.variants[0].supplier_variant_id
        assert first.fulfillment_status == "SUBMITTED"
        assert first.payment_status == "PAID"
    finally: cleanup(db, user, product)


def test_missing_address_fails_without_cj_call(monkeypatch):
    db = SessionLocal(); user, product, order = make_paid_order(db); order.shipping_address = {"city": "Bengaluru"}; db.commit(); fake = FakeCJ(); fake.calls = []
    monkeypatch.setattr("app.services.fulfillment_service.build_supplier_adapter", lambda _: fake)
    monkeypatch.setattr("app.services.fulfillment_service.get_settings", lambda: SimpleNamespace(CJ_API_KEY="configured"))
    try:
        with pytest.raises(BadRequestError, match="missing"):
            asyncio.run(FulfillmentService(db).submit(order.id))
        assert fake.calls == []
    finally: cleanup(db, user, product)


def test_tracking_sync_maps_status_persists_tracking_and_preserves_delivered(monkeypatch):
    db = SessionLocal(); user, product, order = make_paid_order(db); fake = FakeCJ(); fake.calls = []
    monkeypatch.setattr("app.services.fulfillment_service.build_supplier_adapter", lambda _: fake)
    monkeypatch.setattr("app.services.fulfillment_service.get_settings", lambda: SimpleNamespace(CJ_API_KEY="configured"))
    try:
        order.supplier_order_id = f"CJ-ORDER-{product.supplier_product_id}"; order.fulfillment_status = "PROCESSING"; db.commit()
        synced = asyncio.run(FulfillmentService(db).sync_tracking(order.id))
        assert synced.fulfillment_status == "SHIPPED"
        assert synced.tracking_number == "TRACK-1"
        assert synced.tracking_carrier == "Test Carrier"
        assert synced.last_supplier_sync_at is not None
        fake.get_tracking = lambda _: None
        order.fulfillment_status = "DELIVERED"; db.commit()
        delivered = asyncio.run(FulfillmentService(db).sync_tracking(order.id))
        assert delivered.fulfillment_status == "DELIVERED"
    finally: cleanup(db, user, product)


def test_unknown_tracking_status_does_not_downgrade_or_erase_tracking(monkeypatch):
    db = SessionLocal(); user, product, order = make_paid_order(db); fake = FakeCJ()
    async def unknown(_):
        return SupplierTrackingResult(supported=True, supplier_status="mystery", tracking_number=None, carrier=None)
    fake.get_tracking = unknown
    monkeypatch.setattr("app.services.fulfillment_service.build_supplier_adapter", lambda _: fake)
    monkeypatch.setattr("app.services.fulfillment_service.get_settings", lambda: SimpleNamespace(CJ_API_KEY="configured"))
    try:
        order.supplier_order_id = f"CJ-ORDER-{product.supplier_product_id}"; order.fulfillment_status = "SHIPPED"; order.tracking_number = "KEEP-1"; db.commit()
        result = asyncio.run(FulfillmentService(db).sync_tracking(order.id))
        assert result.fulfillment_status == "SHIPPED"
        assert result.tracking_number == "KEEP-1"
        assert result.supplier_status == "mystery"
    finally: cleanup(db, user, product)
