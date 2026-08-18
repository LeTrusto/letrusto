from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.exceptions import NotFoundError
from app.db.session import SessionLocal
from app.models.entities import Order, OrderItem, Product, ProductImage, ProductVariant, User
from app.schemas.account import CustomerAccountDTO
from app.services.order_service import OrderService


def make_fixture(db):
    suffix = uuid4().hex[:8]
    user = User(email=f"account-{suffix}@example.com", full_name="Account Customer")
    other = User(email=f"account-other-{suffix}@example.com", full_name="Other Customer")
    product = Product(
        slug=f"account-product-{suffix}", name="Snapshot Product", description="test", status="ACTIVE",
        supplier="cj", supplier_product_id=f"CJ-{suffix}", price_value=Decimal("100"),
        selling_price=Decimal("100"), ai_score=1, rating=Decimal("1"), ai_summary="", review_summary="",
    )
    image = ProductImage(product=product, url="https://example.test/original.jpg", position=1)
    variant = ProductVariant(product=product, supplier_variant_id=f"VID-{suffix}", supplier_variant_sku=f"SKU-{suffix}", name="Blue", position=1, selling_price=Decimal("100"), cj_inventory=10, active=True)
    db.add_all([user, other, product, image, variant])
    db.commit()
    return user, other, product, variant


def make_order(db, user, product, variant, number):
    order = Order(
        order_number=number, user_id=user.id, status="PENDING_PAYMENT", payment_status="PENDING", fulfillment_status="PENDING",
        subtotal=Decimal("200"), shipping_amount=Decimal("0"), total=Decimal("200"), currency="INR",
        customer_name=user.full_name, customer_email=user.email, customer_phone="9876543210",
        shipping_address={"address": "1 Test Street", "city": "Bengaluru", "state": "Karnataka", "postal_code": "560001", "country": "IN"},
        idempotency_key=f"idempotency-{number}",
        items=[OrderItem(product=product, variant=variant, product_name="Snapshot Product", product_image_url="https://example.test/original.jpg", variant_name="Blue", quantity=2, unit_price=Decimal("100"), line_total=Decimal("200"))],
    )
    db.add(order)
    db.commit()
    return order


def cleanup(db, *entities):
    for entity in entities:
        db.delete(entity)
    db.commit()
    db.close()


def test_customer_lists_only_own_orders_with_pagination_and_snapshot():
    db = SessionLocal()
    user, other, product, variant = make_fixture(db)
    order_one = make_order(db, user, product, variant, f"LT-ACCOUNT-{uuid4().hex[:6]}")
    order_two = make_order(db, user, product, variant, f"LT-ACCOUNT-{uuid4().hex[:6]}")
    other_order = make_order(db, other, product, variant, f"LT-OTHER-{uuid4().hex[:6]}")
    try:
        result = OrderService(db).list_orders(user, page=1, page_size=1)
        assert result.total == 2
        assert len(result.items) == 1
        assert result.has_next is True
        assert result.items[0].items[0].product_image_url == "https://example.test/original.jpg"
        assert other_order.order_number not in {item.order_number for item in result.items}
    finally:
        db.query(Order).filter(Order.id.in_([order_one.id, order_two.id, other_order.id])).delete(synchronize_session=False)
        db.delete(variant)
        db.delete(image := db.query(ProductImage).filter(ProductImage.product_id == product.id).first())
        cleanup(db, user, other, product)


def test_customer_cannot_read_another_customers_order():
    db = SessionLocal()
    user, other, product, variant = make_fixture(db)
    order = make_order(db, user, product, variant, f"LT-OWNERSHIP-{uuid4().hex[:6]}")
    try:
        with pytest.raises(NotFoundError):
            OrderService(db).get_order(other, order.id)
    finally:
        db.delete(order)
        db.delete(variant)
        image = db.query(ProductImage).filter(ProductImage.product_id == product.id).first()
        if image:
            db.delete(image)
        cleanup(db, user, other, product)


def test_customer_account_does_not_expose_internal_id():
    account = CustomerAccountDTO(email="customer@example.test", full_name="Customer", email_verified=False, created_at="2026-08-18T00:00:00+00:00")
    assert "id" not in account.model_dump()
    assert "supplier" not in account.model_dump()
