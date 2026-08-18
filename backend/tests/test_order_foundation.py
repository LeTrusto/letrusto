from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.exceptions import BadRequestError
from app.db.session import SessionLocal
from app.models.entities import Order, Product, ProductVariant, User
from app.schemas.orders import CartItemRequest, CreateOrderRequest, CustomerDetails, ShippingAddress
from app.services.order_service import OrderService


def make_order_fixture(db):
    suffix = uuid4().hex[:10]
    user = User(email=f"order-{suffix}@example.com", full_name="Order Test")
    product = Product(
        slug=f"order-product-{suffix}",
        name="Order test product",
        description="Order test",
        status="ACTIVE",
        supplier="cj",
        supplier_product_id=f"order-cj-{suffix}",
        price_value=Decimal("100.00"),
        selling_price=Decimal("100.00"),
        ai_score=1,
        rating=Decimal("1.0"),
        ai_summary="",
        review_summary="",
    )
    variant = ProductVariant(
        product=product,
        supplier_variant_id=f"VID-{suffix}",
        supplier_variant_sku=f"SKU-{suffix}",
        name="Blue",
        position=1,
        selling_price=Decimal("100.00"),
        cj_inventory=2,
        factory_inventory=999,
        active=True,
    )
    db.add_all([user, product])
    db.commit()
    return user, product, variant


def order_payload(product_slug: str, *, quantity: int = 2, key: str = "order-test-key-001"):
    return CreateOrderRequest(
        items=[CartItemRequest(product_id=product_slug, variant_id="variant-1", quantity=quantity)],
        customer=CustomerDetails(name="Test Buyer", email="buyer@example.com", phone="9876543210"),
        shipping_address=ShippingAddress(
            address="1 Test Street", city="Bengaluru", state="Karnataka", postal_code="560001", country="IN"
        ),
        idempotency_key=key,
    )


def cleanup(db, user, product):
    db.query(Order).filter(Order.user_id == user.id).delete(synchronize_session=False)
    db.delete(user)
    db.delete(product)
    db.commit()
    db.close()


def test_cart_validates_cj_inventory_and_order_snapshots_authoritative_price():
    db = SessionLocal()
    user, product, _ = make_order_fixture(db)
    service = OrderService(db)
    try:
        cart = service.add_cart_item(user, CartItemRequest(product_id=product.slug, variant_id="variant-1", quantity=2))
        assert cart.subtotal == Decimal("200.00")
        with pytest.raises(BadRequestError, match="Only 2 units"):
            service.add_cart_item(user, CartItemRequest(product_id=product.slug, variant_id="variant-1", quantity=1))

        payload = order_payload(product.slug)
        result = service.create_order(user, payload)
        assert result.status == "PENDING_PAYMENT"
        assert result.payment_status == "PENDING"
        assert result.fulfillment_status == "PENDING"
        assert result.subtotal == Decimal("200.00")
        assert result.total == Decimal("200.00")
        assert result.items[0].unit_price == Decimal("100.00")
        assert "supplier" not in result.model_dump_json()
        assert "factory" not in result.model_dump_json()
        assert "VID-" not in result.model_dump_json()

        repeated = service.create_order(user, payload)
        assert repeated.id == result.id
        assert db.query(Order).filter(Order.user_id == user.id).count() == 1
    finally:
        cleanup(db, user, product)


def test_order_revalidates_active_status_and_zero_sellable_inventory():
    db = SessionLocal()
    user, product, variant = make_order_fixture(db)
    service = OrderService(db)
    try:
        variant.cj_inventory = 0
        db.commit()
        with pytest.raises(BadRequestError, match="out of stock"):
            service.create_order(user, order_payload(product.slug))

        variant.cj_inventory = 2
        product.status = "DRAFT"
        db.commit()
        with pytest.raises(Exception, match="Active product"):
            service.create_order(user, order_payload(product.slug, key="order-test-key-002"))
    finally:
        cleanup(db, user, product)
