from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.deps import get_admin_product_service, get_current_admin
from app.db.session import SessionLocal
from app.main import app
from app.models.entities import Product
from app.services.admin_product_service import AdminProductService


VALID_PRICE_INPUTS = {
    "supplier_cost_usd": "10",
    "shipping_cost_usd": "2",
    "usd_to_inr_exchange_rate": "80",
    "platform_fee_percent": "10",
    "payment_fee_percent": "5",
    "rto_reserve_percent": "5",
    "target_margin_percent": "20",
}


def make_product(db) -> Product:
    product = Product(
        id=uuid4(),
        slug=f"phase33-{uuid4()}",
        name="Phase 3.3 product",
        description="Pricing test product",
        status="DRAFT",
        supplier="cj",
        supplier_product_id=f"phase33-{uuid4()}",
        supplier_cost=Decimal("800.00"),
        shipping_cost=Decimal("160.00"),
        selling_price=None,
        currency="INR",
        total_inventory=1050,
        cj_inventory=50,
        factory_inventory=1000,
        verified_warehouse="unverified",
    )
    db.add(product)
    db.commit()
    return product


def test_formula_conversion_cost_lines_margin_and_profit():
    from app.schemas.admin_products import PriceCalculationRequest

    db = SessionLocal()
    product = make_product(db)
    try:
        result = AdminProductService(db).calculate_price(
            product.id, PriceCalculationRequest(**VALID_PRICE_INPUTS)
        )

        assert result.supplier_cost_usd == Decimal("10")
        assert result.shipping_cost_usd == Decimal("2")
        assert result.usd_to_inr_exchange_rate == Decimal("80")
        assert result.base_cost_inr == Decimal("960.00")
        assert result.platform_fee_inr == Decimal("160.00")
        assert result.payment_fee_inr == Decimal("80.00")
        assert result.rto_reserve_inr == Decimal("80.00")
        assert result.target_margin_percent == Decimal("20")
        assert result.target_margin_inr == Decimal("320.00")
        assert result.selling_price_inr == Decimal("1600.00")
        assert result.expected_profit_inr == Decimal("320.00")
        assert result.rounding_rule == "ROUND_HALF_UP_TO_0.01_INR"
        assert db.get(Product, product.id).selling_price == Decimal("1600.00")
    finally:
        db.delete(product)
        db.commit()
        db.close()


def test_selling_price_uses_exact_converted_base_before_rounding():
    from app.services.pricing_engine import calculate_margin_price

    result = calculate_margin_price(
        supplier_cost_usd=Decimal("1"),
        shipping_cost_usd=Decimal("0"),
        usd_to_inr_exchange_rate=Decimal("83.555"),
        platform_fee_percent=Decimal("10"),
        payment_fee_percent=Decimal("5"),
        rto_reserve_percent=Decimal("5"),
        target_margin_percent=Decimal("10"),
    )

    assert result.base_cost_inr == Decimal("83.56")
    assert result.selling_price_inr == Decimal("119.36")


def test_calculation_is_deterministic_and_preserves_catalog_state():
    from app.schemas.admin_products import PriceCalculationRequest

    db = SessionLocal()
    product = make_product(db)
    service = AdminProductService(db)
    before = (
        product.status,
        product.supplier_cost,
        product.shipping_cost,
        product.total_inventory,
        product.cj_inventory,
        product.factory_inventory,
        product.verified_warehouse,
        product.last_supplier_sync_at,
    )
    try:
        payload = PriceCalculationRequest(**VALID_PRICE_INPUTS)
        first = service.calculate_price(product.id, payload)
        second = service.calculate_price(product.id, payload)
        db.refresh(product)

        assert first == second
        assert product.status == "DRAFT"
        assert (
            product.status,
            product.supplier_cost,
            product.shipping_cost,
            product.total_inventory,
            product.cj_inventory,
            product.factory_inventory,
            product.verified_warehouse,
            product.last_supplier_sync_at,
        ) == before
    finally:
        db.delete(product)
        db.commit()
        db.close()


@pytest.mark.parametrize(
    "changes",
    [
        {"supplier_cost_usd": "-1"},
        {"shipping_cost_usd": "-1"},
        {"usd_to_inr_exchange_rate": "0"},
        {"usd_to_inr_exchange_rate": "-1"},
        {"platform_fee_percent": "-1"},
        {"payment_fee_percent": "100"},
        {"rto_reserve_percent": "-1"},
        {"target_margin_percent": "100"},
    ],
)
def test_request_rejects_negative_costs_invalid_exchange_and_percentages(changes):
    from app.schemas.admin_products import PriceCalculationRequest

    payload = {**VALID_PRICE_INPUTS, **changes}
    with pytest.raises(ValidationError):
        PriceCalculationRequest(**payload)


@pytest.mark.parametrize(
    ("missing_field", "expected_detail"),
    [
        ("supplier_cost", "Supplier cost is missing"),
        ("shipping_cost", "Shipping cost is missing"),
    ],
)
def test_route_rejects_missing_stored_supplier_economics(missing_field, expected_detail):
    db = SessionLocal()
    product = make_product(db)
    setattr(product, missing_field, None)
    db.commit()
    app.dependency_overrides[get_current_admin] = lambda: object()
    app.dependency_overrides[get_admin_product_service] = lambda: AdminProductService(db)
    try:
        response = TestClient(app).post(
            f"/api/v1/admin/products/{product.id}/calculate-price", json=VALID_PRICE_INPUTS
        )

        assert response.status_code == 400
        assert response.json()["detail"] == expected_detail
        db.refresh(product)
        assert product.selling_price is None
    finally:
        app.dependency_overrides.clear()
        db.delete(product)
        db.commit()
        db.close()


def test_route_requires_every_input_and_rejects_combined_percentage_at_100():
    db = SessionLocal()
    product = make_product(db)
    app.dependency_overrides[get_current_admin] = lambda: object()
    app.dependency_overrides[get_admin_product_service] = lambda: AdminProductService(db)
    client = TestClient(app)
    try:
        missing = client.post(f"/api/v1/admin/products/{product.id}/calculate-price", json={})
        assert missing.status_code == 422
        assert {error["loc"][-1] for error in missing.json()["detail"]} >= {
            "supplier_cost_usd",
            "shipping_cost_usd",
            "usd_to_inr_exchange_rate",
            "platform_fee_percent",
            "payment_fee_percent",
            "rto_reserve_percent",
            "target_margin_percent",
        }

        invalid = {**VALID_PRICE_INPUTS, "platform_fee_percent": "50", "target_margin_percent": "40"}
        response = client.post(
            f"/api/v1/admin/products/{product.id}/calculate-price", json=invalid
        )
        assert response.status_code == 400
        assert "less than 100" in response.json()["detail"]
        db.refresh(product)
        assert product.selling_price is None
    finally:
        app.dependency_overrides.clear()
        db.delete(product)
        db.commit()
        db.close()


def test_protected_route_calculates_without_supplier_calls():
    db = SessionLocal()
    product = make_product(db)
    app.dependency_overrides[get_current_admin] = lambda: object()
    app.dependency_overrides[get_admin_product_service] = lambda: AdminProductService(db)
    try:
        response = TestClient(app).post(
            f"/api/v1/admin/products/{product.id}/calculate-price", json=VALID_PRICE_INPUTS
        )
        assert response.status_code == 200
        assert response.json()["selling_price_inr"] == "1600.00"
        assert response.json()["currency"] == "INR"
    finally:
        app.dependency_overrides.clear()
        db.delete(product)
        db.commit()
        db.close()


def test_route_requires_admin():
    response = TestClient(app).post(
        f"/api/v1/admin/products/{uuid4()}/calculate-price", json=VALID_PRICE_INPUTS
    )
    assert response.status_code == 401