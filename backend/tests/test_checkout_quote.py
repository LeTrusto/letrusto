from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.db.session import SessionLocal
from app.models.entities import Order, PrintfulShippingRate, Product, ProductVariant, User
from app.schemas.orders import CartItemRequest, OrderQuoteRequest
from app.services.order_service import OrderService

HOODIE_PRICE = Decimal("4499.00")


def make_hoodie(db, *, requires_verification: bool = True):
    suffix = uuid4().hex[:10]
    user = User(email=f"quote-{suffix}@example.com", full_name="Quote Test")
    product = Product(
        slug=f"hoodie-{suffix}",
        name="Unisex Hoodie",
        description="Hoodie",
        status="ACTIVE",
        supplier="printful",
        supplier_product_id=f"printful-{suffix}",
        price_value=HOODIE_PRICE,
        selling_price=HOODIE_PRICE,
        ai_score=1,
        rating=Decimal("1.0"),
        ai_summary="",
        review_summary="",
    )
    ProductVariant(
        product=product,
        supplier_variant_id=f"VID-{suffix}",
        supplier_variant_sku=f"SKU-{suffix}",
        name="Black / M",
        position=1,
        selling_price=HOODIE_PRICE,
        cj_inventory=10,
        factory_inventory=0,
        active=True,
    )
    db.add_all([user, product])
    db.flush()
    now = datetime.now(timezone.utc)
    rate = PrintfulShippingRate(
        product_id=product.id,
        source="printful",
        rate_source="LETRUSTO_ESTIMATE" if requires_verification else "verified",
        destination_region="IN",
        category_key="hoodies-sweatshirts",
        country_codes=[],
        shipping_method="Standard",
        single_product_rate=Decimal("299") if requires_verification else Decimal("1733.62"),
        additional_product_rate=Decimal("100") if requires_verification else Decimal("784.00"),
        currency="INR",
        effective_at=now,
        updated_at=now,
        active=True,
        requires_verification=requires_verification,
        supplier_single_product_rate=None if requires_verification else Decimal("17.69"),
        supplier_additional_product_rate=None if requires_verification else Decimal("8.00"),
        supplier_currency=None if requires_verification else "USD",
        supplier_to_customer_fx_rate=None if requires_verification else Decimal("98.00"),
    )
    db.add(rate)
    db.commit()
    return user, product, rate


def cleanup(db, user, product, rate):
    db.query(Order).filter(Order.user_id == user.id).delete(synchronize_session=False)
    db.delete(rate)
    db.delete(user)
    db.delete(product)
    db.commit()
    db.close()


def quote_request(product_slug: str, quantity: int, country: str = "IN") -> OrderQuoteRequest:
    return OrderQuoteRequest(
        items=[CartItemRequest(product_id=product_slug, variant_id="variant-1", quantity=quantity)],
        country=country,
    )


@pytest.mark.parametrize(
    ("quantity", "shipping"),
    [(1, Decimal("1733.62")), (2, Decimal("2517.62")), (3, Decimal("3301.62"))],
)
def test_india_hoodie_quote_charges_first_and_additional_shipping(quantity, shipping):
    db = SessionLocal()
    user, product, rate = make_hoodie(db, requires_verification=False)
    try:
        quote = OrderService(db).quote_order(user, quote_request(product.slug, quantity))
        assert quote.currency == "INR"
        assert quote.subtotal == HOODIE_PRICE * quantity
        assert quote.shipping_amount == shipping
        assert quote.total == quote.subtotal + quote.shipping_amount
        assert quote.shipping_status == "AVAILABLE"
        assert quote.purchasable is True
        assert quote.shipping_message is None
    finally:
        cleanup(db, user, product, rate)


def test_quote_never_reports_zero_shipping_when_rate_is_missing(monkeypatch):
    db = SessionLocal()
    user, product, rate = make_hoodie(db, requires_verification=False)
    monkeypatch.setattr(
        "app.services.order_service.PrintfulShippingService.estimate",
        lambda *_args, **_kwargs: {"status": "REQUIRES_VERIFICATION", "message": "Shipping rate requires Printful verification"},
    )
    try:
        quote = OrderService(db).quote_order(user, quote_request(product.slug, 1))
        assert quote.shipping_status == "REQUIRES_VERIFICATION"
        assert quote.purchasable is False
        assert quote.shipping_amount == Decimal("0")
        assert quote.total == quote.subtotal
    finally:
        cleanup(db, user, product, rate)


def test_international_quote_is_not_purchasable_and_stays_inr():
    db = SessionLocal()
    user, product, rate = make_hoodie(db)
    try:
        quote = OrderService(db).quote_order(user, quote_request(product.slug, 2, country="US"))
        assert quote.currency == "INR"
        assert quote.purchasable is False
        assert quote.unavailable_reason == "INTERNATIONAL_CHECKOUT_UNAVAILABLE"
        assert quote.shipping_amount == Decimal("0")
    finally:
        cleanup(db, user, product, rate)


def test_unsupported_destination_is_reported_without_shipping_charge():
    db = SessionLocal()
    user, product, rate = make_hoodie(db)
    try:
        service = OrderService(db)
        status, amount, message = service._shipping_quote(
            service._resolve_items(quote_request(product.slug, 1).items), "ZZ", "INR"
        )
        assert status == "UNSUPPORTED_DESTINATION"
        assert amount == Decimal("0")
        assert message
    finally:
        cleanup(db, user, product, rate)


def test_shipping_currency_mismatch_is_reported_as_invalid_configuration():
    db = SessionLocal()
    user, product, rate = make_hoodie(db, requires_verification=False)
    try:
        service = OrderService(db)
        status, amount, _ = service._shipping_quote(
            service._resolve_items(quote_request(product.slug, 1).items), "IN", "USD"
        )
        assert status == "INVALID_CONFIGURATION"
        assert amount == Decimal("0")
    finally:
        cleanup(db, user, product, rate)


def test_quote_charges_shipping_once_per_line_item():
    db = SessionLocal()
    user, product, rate = make_hoodie(db, requires_verification=False)
    try:
        service = OrderService(db)
        single = service.quote_order(user, quote_request(product.slug, 1))
        double = service.quote_order(user, quote_request(product.slug, 2))
        assert double.shipping_amount - single.shipping_amount == Decimal("784.00")
    finally:
        cleanup(db, user, product, rate)
