from decimal import Decimal
import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.exceptions import BadRequestError
from app.db.session import SessionLocal
from app.models.entities import Cart, CartItem, Order, OrderItem, PaymentAttempt, Product, ProductVariant, SupplierVariantInventory, User
from app.api.deps import get_current_admin, get_fulfillment_service
from app.main import app
from fastapi.testclient import TestClient
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

    async def get_order_status(self, supplier_order_id):
        return SupplierOrderResult(accepted=True, supplier_order_id=supplier_order_id, status="AWAITING_PAYMENT", supplier_status="UNPAID")

    async def get_balance(self):
        from app.suppliers.base import SupplierBalanceResult
        return SupplierBalanceResult(supported=True, amount_usd=100.0, freeze_amount_usd=0.0)

    async def pay_balance(self, shipment_order_id, pay_id=None):
        return SupplierOrderResult(accepted=True, supplier_order_id="CJ-EXPLICIT", shipment_order_id=shipment_order_id, status="AWAITING_PAYMENT", supplier_status="UNPAID", payment_state="PENDING", pay_id="PAY-EXPLICIT")


def make_paid_order(db):
    suffix = uuid4().hex[:8]
    user = User(email=f"fulfillment-{suffix}@example.com", full_name="Fulfillment Test")
    product = Product(slug=f"fulfillment-product-{suffix}", name="Fulfillment product", description="test", status="ACTIVE", supplier="cj", supplier_product_id=f"CJ-PID-{suffix}", price_value=Decimal("100"), selling_price=Decimal("100"), ai_score=1, rating=Decimal("1"), ai_summary="", review_summary="")
    variant = ProductVariant(product=product, supplier_variant_id=f"CJ-VID-{suffix}", supplier_variant_sku=f"CJ-SKU-{suffix}", name="Blue", attributes="Blue", position=1, selling_price=Decimal("100"), cj_inventory=2, factory_inventory=999)
    db.add_all([user, product]); db.flush()
    db.add(SupplierVariantInventory(product_id=product.id, variant_id=variant.id, supplier_product_id=product.supplier_product_id, supplier_variant_id=variant.supplier_variant_id, warehouse_identity=f"CN-{suffix}", warehouse_country="CN", storage_id="CN", warehouse_name="China Warehouse", total_inventory=2, cj_sellable_inventory=2, factory_inventory=999)); db.commit()
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


def test_admin_supplier_payment_action_is_explicit_and_persists_state(monkeypatch):
    db = SessionLocal(); user, product, order = make_paid_order(db); fake = FakeCJ()
    order.supplier_order_id = "CJ-EXPLICIT"
    order.supplier_shipment_order_id = "SHIP-EXPLICIT"
    order.supplier_status = "UNPAID"
    order.supplier_payment_state = "AWAITING_PAYMENT"
    db.commit()
    monkeypatch.setattr("app.services.fulfillment_service.build_supplier_adapter", lambda _: fake)
    monkeypatch.setattr("app.services.fulfillment_service.get_settings", lambda: SimpleNamespace(CJ_API_KEY="configured"))
    service = FulfillmentService(db)
    app.dependency_overrides[get_current_admin] = lambda: object()
    app.dependency_overrides[get_fulfillment_service] = lambda: service
    try:
        response = TestClient(app).post(f"/api/v1/admin/orders/{order.id}/supplier-payment", json={"required_amount_usd": 25})
        assert response.status_code == 200
        body = response.json()
        assert body["supplier_order_id"] == "CJ-EXPLICIT"
        assert body["payment_state"] == "PENDING"
        assert body["confirmation_required"] is True
        db.refresh(order)
        assert order.supplier_pay_id == "PAY-EXPLICIT"
        assert order.supplier_payment_state == "PENDING"
    finally:
        app.dependency_overrides.clear()
        cleanup(db, user, product)
