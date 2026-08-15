from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.deps import get_admin_product_service, get_current_admin
from app.db.session import SessionLocal
from app.main import app
from app.models.entities import Product, ProductVariant
from app.services.admin_product_service import AdminProductService


def make_variant_product(db) -> tuple[Product, list[ProductVariant]]:
    product = Product(
        id=uuid4(),
        slug=f"phase332-{uuid4()}",
        name="Phase 3.3.2 product",
        description="Variant pricing test product",
        status="DRAFT",
        supplier="cj",
        supplier_product_id=f"phase332-{uuid4()}",
        supplier_cost=None,
        shipping_cost=Decimal("242.15"),
        selling_price=None,
        currency="INR",
        total_inventory=110,
        cj_inventory=10,
        factory_inventory=100,
    )
    variants = [
        ProductVariant(
            product=product,
            supplier_variant_id="VID-LOW",
            supplier_variant_sku="SKU-LOW",
            supplier_cost=None,
            supplier_cost_usd=Decimal("0.70"),
            total_inventory=55,
            cj_inventory=5,
            factory_inventory=50,
            position=1,
        ),
        ProductVariant(
            product=product,
            supplier_variant_id="VID-HIGH",
            supplier_variant_sku="SKU-HIGH",
            supplier_cost=None,
            supplier_cost_usd=Decimal("1.09"),
            total_inventory=55,
            cj_inventory=5,
            factory_inventory=50,
            position=2,
        ),
    ]
    db.add(product)
    db.commit()
    return product, variants


def delete_product(db, product: Product) -> None:
    db.delete(product)
    db.commit()
    db.close()


def test_variant_prices_are_independent_and_preserve_catalog_state():
    db = SessionLocal()
    product, variants = make_variant_product(db)
    supplier_costs_before = [variant.supplier_cost for variant in variants]
    catalog_before = (
        product.status,
        product.supplier_cost,
        product.selling_price,
        product.total_inventory,
        product.cj_inventory,
        product.factory_inventory,
    )
    try:
        first = AdminProductService(db).calculate_variant_prices(product.id)
        second = AdminProductService(db).calculate_variant_prices(product.id)
        db.refresh(product)
        for variant in variants:
            db.refresh(variant)

        assert first == second
        assert [item.supplier_cost_usd for item in first.variants] == [Decimal("0.70"), Decimal("1.09")]
        assert [item.selling_price_inr for item in first.variants] == [Decimal("421.99"), Decimal("473.89")]
        assert [variant.selling_price for variant in variants] == [Decimal("421.99"), Decimal("473.89")]
        assert all(item.shipping_cost_inr == Decimal("242.15") for item in first.variants)
        assert all(item.denominator == Decimal("0.7364") for item in first.variants)
        assert [variant.supplier_cost for variant in variants] == supplier_costs_before
        assert (
            product.status,
            product.supplier_cost,
            product.selling_price,
            product.total_inventory,
            product.cj_inventory,
            product.factory_inventory,
        ) == catalog_before
    finally:
        delete_product(db, product)


def test_missing_source_usd_cost_rejects_without_partial_persistence():
    from app.core.exceptions import BadRequestError

    db = SessionLocal()
    product, variants = make_variant_product(db)
    variants[0].selling_price = Decimal("399.00")
    variants[1].supplier_cost_usd = None
    db.commit()
    try:
        try:
            AdminProductService(db).calculate_variant_prices(product.id)
            raise AssertionError("Expected missing source cost to fail")
        except BadRequestError as exc:
            assert "Source USD supplier cost is missing" in str(exc)

        db.refresh(variants[0])
        db.refresh(variants[1])
        assert variants[0].selling_price == Decimal("399.00")
        assert variants[1].selling_price is None
    finally:
        delete_product(db, product)


def test_missing_shipping_is_rejected_without_persistence():
    from app.core.exceptions import BadRequestError

    db = SessionLocal()
    product, variants = make_variant_product(db)
    product.shipping_cost = None
    db.commit()
    try:
        try:
            AdminProductService(db).calculate_variant_prices(product.id)
            raise AssertionError("Expected missing shipping cost to fail")
        except BadRequestError as exc:
            assert "Stored shipping cost is missing" in str(exc)

        for variant in variants:
            db.refresh(variant)
            assert variant.selling_price is None
    finally:
        delete_product(db, product)


def test_variant_route_uses_stored_costs_and_is_protected():
    db = SessionLocal()
    product, variants = make_variant_product(db)
    app.dependency_overrides[get_current_admin] = lambda: object()
    app.dependency_overrides[get_admin_product_service] = lambda: AdminProductService(db)
    client = TestClient(app)
    try:
        response = client.post(
            f"/api/v1/admin/products/{product.id}/calculate-variant-prices"
        )

        assert response.status_code == 200
        result = response.json()["variants"]
        assert [item["supplier_cost_usd"] for item in result] == ["0.7000", "1.0900"]
        assert all(item["target_margin_status"] == "TARGET_MARGIN_MET" for item in result)
        assert all(item["cac_target_status"] == "CAC_TARGET_NOT_SUPPORTED" for item in result)
    finally:
        app.dependency_overrides.clear()
        delete_product(db, product)

    unauthenticated = TestClient(app).post(
        f"/api/v1/admin/products/{uuid4()}/calculate-variant-prices"
    )
    assert unauthenticated.status_code == 401


def test_variant_route_openapi_has_no_business_input_body():
    operation = app.openapi()["paths"][
        "/api/v1/admin/products/{product_id}/calculate-variant-prices"
    ]["post"]

    assert "requestBody" not in operation