from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_admin_product_service, get_current_admin
from app.db.session import SessionLocal
from app.main import app
from app.models.entities import Product, ProductImage, ProductVariant
from app.services.admin_product_service import AdminProductService
from app.services.commercial_review_service import evaluate_commercial_product
from app.services.launch_pricing_policy import load_launch_pricing_policy


def test_complete_variant_priced_product_with_validation_pass_is_approved():
    product = complete_product()

    result = evaluate_commercial_product(product, load_launch_pricing_policy())

    assert result.decision == "APPROVED"
    assert result.blocking_reasons == []
    assert result.reasons == ["CAC_TARGET_NOT_SUPPORTED"]
    assert result.market_price_status == "NOT_EVALUATED"
    assert result.active_variant_count == 1
    assert result.valid_variant_count == 1
    assert result.missing_variant_count == 0
    assert result.target_margin_met_count == 1


def complete_product(**overrides):
    values = dict(
        name="Commercial product",
        description="Complete stored supplier product",
        supplier="cj",
        supplier_product_id="CJ-COMMERCIAL-1",
        shipping_cost=Decimal("242.15"),
        cj_inventory=40,
        images=[SimpleNamespace(url="https://example.com/product.jpg")],
        variants=[
            SimpleNamespace(
                active=True,
                supplier_variant_id="CJ-VARIANT-1",
                supplier_variant_sku="CJ-SKU-1",
                supplier_cost_usd=Decimal("0.70"),
                selling_price=Decimal("421.99"),
            )
        ],
        supplier_validation_status="PASS",
    )
    values.update(overrides)
    return SimpleNamespace(**values)


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        ({"supplier_cost_usd": None}, "SUPPLIER_COST_MISSING"),
        ({"selling_price": None}, "VARIANT_PRICE_MISSING"),
        ({"selling_price": Decimal("400.00")}, "VARIANT_PRICE_DISCREPANCY"),
    ],
)
def test_all_active_variant_costs_prices_and_economics_are_required(change, reason):
    product = complete_product()
    for field, value in change.items():
        setattr(product.variants[0], field, value)

    result = evaluate_commercial_product(product, load_launch_pricing_policy())

    assert result.decision == "REVIEW"
    assert reason in result.reasons
    if change.get("selling_price") == Decimal("400.00"):
        assert "TARGET_MARGIN_NOT_MET" in result.reasons


@pytest.mark.parametrize(
    ("shipping_cost", "reason"),
    [(None, "SHIPPING_COST_MISSING"), (Decimal("-0.01"), "SHIPPING_COST_INVALID")],
)
def test_shipping_must_be_present_and_nonnegative(shipping_cost, reason):
    result = evaluate_commercial_product(
        complete_product(shipping_cost=shipping_cost), load_launch_pricing_policy()
    )

    assert result.decision == "REVIEW"
    assert reason in result.reasons


def test_all_active_variants_are_evaluated_but_inactive_variants_do_not_block():
    product = complete_product()
    product.variants.extend([
        SimpleNamespace(
            active=True, supplier_variant_id="CJ-VARIANT-2", supplier_variant_sku="CJ-SKU-2",
            supplier_cost_usd=Decimal("1.09"), selling_price=None,
        ),
        SimpleNamespace(
            active=False, supplier_variant_id="CJ-VARIANT-3", supplier_variant_sku="CJ-SKU-3",
            supplier_cost_usd=None, selling_price=None,
        ),
    ])

    result = evaluate_commercial_product(product, load_launch_pricing_policy())

    assert result.decision == "REVIEW"
    assert result.active_variant_count == 2
    assert result.valid_variant_count == 1
    assert result.missing_variant_count == 1
    assert result.cac_target_supported is False


def test_factory_inventory_never_substitutes_for_sellable_cj_inventory():
    product = complete_product(cj_inventory=0)
    product.factory_inventory = 77651

    result = evaluate_commercial_product(product, load_launch_pricing_policy())

    assert result.decision == "REVIEW"
    assert "NO_SELLABLE_INVENTORY" in result.reasons


@pytest.mark.parametrize("field", ["name", "description", "supplier", "supplier_product_id"])
def test_required_product_data_is_complete(field):
    result = evaluate_commercial_product(
        complete_product(**{field: ""}), load_launch_pricing_policy()
    )

    assert result.decision == "REVIEW"
    assert "INCOMPLETE_PRODUCT_DATA" in result.reasons


def test_images_variants_and_supplier_variant_identifiers_are_required():
    products = [
        complete_product(images=[]),
        complete_product(variants=[]),
        complete_product(),
    ]
    products[-1].variants[0].supplier_variant_sku = ""

    for product in products:
        result = evaluate_commercial_product(product, load_launch_pricing_policy())
        assert result.decision == "REVIEW"
        assert "INCOMPLETE_PRODUCT_DATA" in result.reasons


@pytest.mark.parametrize(
    ("validation_status", "decision", "reason"),
    [
        (None, "REVIEW", "VALIDATION_NOT_AVAILABLE"),
        ("REVIEW", "REVIEW", "SUPPLIER_VALIDATION_REVIEW"),
        ("REJECT", "REJECTED", "SUPPLIER_VALIDATION_REJECTED"),
        ("PASS", "APPROVED", None),
    ],
)
def test_commercial_review_consumes_persisted_phase2_verdict(validation_status, decision, reason):
    result = evaluate_commercial_product(
        complete_product(
            supplier_validation_status=validation_status,
            supplier_validation_score=61,
            supplier_validation_notes=["Persisted evidence"],
        ),
        load_launch_pricing_policy(),
    )

    assert result.decision == decision
    assert (reason is None) or reason in result.reasons
    assert result.supplier_validation_status == validation_status
    assert result.supplier_validation_score == 61
    assert result.supplier_validation_issues == ["Persisted evidence"]


def test_cac_unsupported_and_market_not_evaluated_do_not_block_approval():
    result = evaluate_commercial_product(complete_product(), load_launch_pricing_policy())

    assert result.decision == "APPROVED"
    assert result.cac_target_supported is False
    assert result.cac_target_status == "CAC_TARGET_NOT_SUPPORTED"
    assert result.market_price_status == "NOT_EVALUATED"


def test_protected_route_persists_only_commercial_decision_and_is_deterministic():
    db = SessionLocal()
    service = AdminProductService(db)
    product = Product(
        id=uuid4(), slug=f"phase34-{uuid4()}", name="Commercial route product",
        description="Complete route test product", status="DRAFT", supplier="cj",
        supplier_product_id=f"CJ-{uuid4()}", shipping_cost=Decimal("242.15"),
        cj_inventory=40, factory_inventory=77651, total_inventory=77691,
        supplier_validation_status=None,
    )
    db.add(product)
    db.flush()
    db.add(ProductImage(product_id=product.id, url="https://example.com/route.jpg", position=1))
    variant = ProductVariant(
        product_id=product.id, supplier_variant_id="CJ-ROUTE-V1", supplier_variant_sku="CJ-ROUTE-S1",
        name="Route variant", supplier_cost=Decimal("58.45"), supplier_cost_usd=Decimal("0.70"),
        selling_price=Decimal("421.99"), total_inventory=77691, cj_inventory=40,
        factory_inventory=77651, active=True, position=1,
    )
    db.add(variant)
    db.commit()
    protected_product = (
        product.status, product.shipping_cost, product.cj_inventory, product.factory_inventory,
        product.total_inventory, product.supplier, product.supplier_product_id, product.last_supplier_sync_at,
    )
    protected_variant = (
        variant.supplier_cost, variant.supplier_cost_usd, variant.selling_price,
        variant.cj_inventory, variant.factory_inventory, variant.total_inventory,
    )
    client = TestClient(app)
    try:
        unauthorized = client.post(f"/api/v1/admin/products/{product.id}/commercial-review")
        assert unauthorized.status_code == 401

        app.dependency_overrides[get_current_admin] = lambda: object()
        app.dependency_overrides[get_admin_product_service] = lambda: service
        first = client.post(f"/api/v1/admin/products/{product.id}/commercial-review")
        second = client.post(f"/api/v1/admin/products/{product.id}/commercial-review")

        assert first.status_code == 200
        assert first.json()["decision"] == "REVIEW"
        assert first.json()["reasons"] == ["VALIDATION_NOT_AVAILABLE", "CAC_TARGET_NOT_SUPPORTED"]
        assert first.json()["supplier_validation_status"] is None
        assert first.json()["supplier_validation_score"] is None
        assert first.json()["supplier_validation_issues"] == []
        assert second.json()["decision"] == first.json()["decision"]
        assert second.json()["reasons"] == first.json()["reasons"]
        db.refresh(product)
        db.refresh(variant)
        assert product.commercial_status == "REVIEW"
        assert product.commercial_reasons == first.json()["reasons"]
        assert product.commercial_reviewed_at is not None
        assert (
            product.status, product.shipping_cost, product.cj_inventory, product.factory_inventory,
            product.total_inventory, product.supplier, product.supplier_product_id, product.last_supplier_sync_at,
        ) == protected_product
        assert (
            variant.supplier_cost, variant.supplier_cost_usd, variant.selling_price,
            variant.cj_inventory, variant.factory_inventory, variant.total_inventory,
        ) == protected_variant
        assert db.query(Product).filter(Product.id == product.id).count() == 1
        assert db.query(ProductVariant).filter(ProductVariant.product_id == product.id).count() == 1
    finally:
        app.dependency_overrides.clear()
        db.delete(product)
        db.commit()
        db.close()