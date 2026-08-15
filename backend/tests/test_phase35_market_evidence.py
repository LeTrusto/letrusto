from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_admin_product_service, get_current_admin
from app.db.session import SessionLocal
from app.main import app
from app.models.entities import Product, ProductMarketEvidence, ProductVariant
from app.schemas.admin_products import MarketEvidenceCreate
from app.services.admin_product_service import AdminProductService


@pytest.fixture
def market_context():
    db = SessionLocal()
    product = Product(
        id=uuid4(), slug=f"phase35-{uuid4()}", name="Phase 3.5 product",
        description="Fixture only", status="DRAFT", supplier="cj",
        supplier_product_id=f"phase35-{uuid4()}", supplier_cost=Decimal("91.02"),
        shipping_cost=Decimal("167.00"), selling_price=Decimal("519.00"),
        commercial_status="REVIEW", cj_inventory=40, factory_inventory=77651,
    )
    other_product = Product(
        id=uuid4(), slug=f"phase35-other-{uuid4()}", name="Other product",
        description="Fixture only", status="DRAFT", supplier="cj",
        supplier_product_id=f"phase35-other-{uuid4()}",
    )
    db.add_all([product, other_product])
    db.commit()
    service = AdminProductService(db)
    app.dependency_overrides[get_current_admin] = lambda: object()
    app.dependency_overrides[get_admin_product_service] = lambda: service
    client = TestClient(app)
    yield db, service, client, product, other_product
    app.dependency_overrides.clear()
    for candidate in (product, other_product):
        stored = db.get(Product, candidate.id)
        if stored:
            db.delete(stored)
    db.commit()
    db.close()


def payload(price: str = "399", **overrides):
    data = {
        "competitor_name": "Fixture competitor", "product_name": "Fixture product",
        "source_url": "https://example.com/products/fixture", "observed_price_inr": price,
        "currency": "INR", "variant_description": "Blue / small",
        "notes": "Manual fixture observation",
    }
    data.update(overrides)
    return data


def add_evidence(service, product_id, price: str = "399"):
    return service.create_market_evidence(product_id, MarketEvidenceCreate(**payload(price)))


def add_variant(db, product_id, variant_id: str, price: str | None, *, active: bool = True):
    variant = ProductVariant(
        product_id=product_id, supplier_variant_id=variant_id, supplier_variant_sku=variant_id,
        name=variant_id, attributes="fixture",
        selling_price=Decimal(price) if price is not None else None, active=active,
    )
    db.add(variant)
    db.commit()
    return variant


def test_create_market_evidence_persists_manual_fields(market_context):
    db, _, client, product, _ = market_context
    checked_at = datetime(2026, 8, 15, 10, 30, tzinfo=timezone.utc)
    response = client.post(
        f"/api/v1/admin/products/{product.id}/market-evidence",
        json=payload(checked_at=checked_at.isoformat()),
    )
    assert response.status_code == 200
    stored = db.get(ProductMarketEvidence, response.json()["id"])
    assert stored.product_id == product.id
    assert stored.competitor_name == "Fixture competitor"
    assert stored.product_name == "Fixture product"
    assert stored.source_url == "https://example.com/products/fixture"
    assert stored.observed_price_inr == Decimal("399.00")
    assert stored.currency == "INR"
    assert stored.variant_description == "Blue / small"
    assert stored.notes == "Manual fixture observation"
    assert stored.checked_at == checked_at
    assert stored.created_at is not None and stored.updated_at is not None


def test_create_rejects_blank_competitor_name(market_context):
    _, _, client, product, _ = market_context
    assert client.post(f"/api/v1/admin/products/{product.id}/market-evidence", json=payload(competitor_name="   ")).status_code == 422


def test_create_rejects_blank_product_name(market_context):
    _, _, client, product, _ = market_context
    assert client.post(f"/api/v1/admin/products/{product.id}/market-evidence", json=payload(product_name=" ")).status_code == 422


def test_create_requires_source_url(market_context):
    _, _, client, product, _ = market_context
    request = payload()
    request.pop("source_url")
    assert client.post(f"/api/v1/admin/products/{product.id}/market-evidence", json=request).status_code == 422


def test_create_rejects_invalid_source_url(market_context):
    _, _, client, product, _ = market_context
    assert client.post(f"/api/v1/admin/products/{product.id}/market-evidence", json=payload(source_url="not-a-url")).status_code == 422


def test_create_rejects_zero_price(market_context):
    _, _, client, product, _ = market_context
    assert client.post(f"/api/v1/admin/products/{product.id}/market-evidence", json=payload("0")).status_code == 422


def test_create_rejects_negative_price(market_context):
    _, _, client, product, _ = market_context
    assert client.post(f"/api/v1/admin/products/{product.id}/market-evidence", json=payload("-1")).status_code == 422


def test_create_rejects_non_inr_currency(market_context):
    _, _, client, product, _ = market_context
    assert client.post(f"/api/v1/admin/products/{product.id}/market-evidence", json=payload(currency="USD")).status_code == 422


def test_get_lists_product_evidence_only(market_context):
    _, service, client, product, other_product = market_context
    own = add_evidence(service, product.id, "399")
    add_evidence(service, other_product.id, "499")
    response = client.get(f"/api/v1/admin/products/{product.id}/market-evidence")
    assert response.status_code == 200
    assert [item["id"] for item in response.json()["evidence"]] == [str(own.id)]


def test_delete_removes_owned_evidence(market_context):
    db, service, client, product, _ = market_context
    evidence = add_evidence(service, product.id)
    response = client.delete(f"/api/v1/admin/products/{product.id}/market-evidence/{evidence.id}")
    assert response.status_code == 204
    assert db.get(ProductMarketEvidence, evidence.id) is None


def test_delete_rejects_evidence_owned_by_another_product(market_context):
    db, service, client, product, other_product = market_context
    evidence = add_evidence(service, product.id)
    response = client.delete(f"/api/v1/admin/products/{other_product.id}/market-evidence/{evidence.id}")
    assert response.status_code == 404
    assert db.get(ProductMarketEvidence, evidence.id) is not None


def test_create_for_unknown_product_returns_404(market_context):
    _, _, client, _, _ = market_context
    assert client.post(f"/api/v1/admin/products/{uuid4()}/market-evidence", json=payload()).status_code == 404


def test_statistics_for_399_449_499(market_context):
    _, service, _, product, _ = market_context
    for price in ("399", "449", "499"):
        add_evidence(service, product.id, price)
    analysis = service.get_market_evidence(product.id).analysis
    assert analysis.observation_count == 3
    assert analysis.minimum_price_inr == Decimal("399.00")
    assert analysis.maximum_price_inr == Decimal("499.00")
    assert analysis.average_price_inr == Decimal("449.00")
    assert analysis.median_price_inr == Decimal("449.00")


def test_zero_observations_is_insufficient_with_null_statistics(market_context):
    _, service, _, product, _ = market_context
    analysis = service.get_market_evidence(product.id).analysis
    assert analysis.observation_count == 0
    assert analysis.status == "INSUFFICIENT_MARKET_DATA"
    assert analysis.minimum_price_inr is None
    assert analysis.maximum_price_inr is None
    assert analysis.average_price_inr is None
    assert analysis.median_price_inr is None


def test_one_observation_is_insufficient(market_context):
    _, service, _, product, _ = market_context
    add_evidence(service, product.id)
    assert service.get_market_evidence(product.id).analysis.status == "INSUFFICIENT_MARKET_DATA"


def test_two_observations_enable_competitive_comparison(market_context):
    db, service, _, product, _ = market_context
    add_variant(db, product.id, "competitive", "449")
    add_evidence(service, product.id, "399")
    add_evidence(service, product.id, "499")
    assert service.get_market_evidence(product.id).analysis.status == "MARKET_COMPETITIVE"


def test_authoritative_product_price_is_compared_when_variants_are_unpriced(market_context):
    _, service, _, product, _ = market_context
    add_evidence(service, product.id, "399")
    add_evidence(service, product.id, "499")

    analysis = service.get_market_evidence(product.id).analysis

    assert analysis.status == "MARKET_ABOVE_OBSERVED"
    assert analysis.evaluated_variant_count == 0
    assert analysis.stored_product_selling_price_inr == Decimal("519.00")


def test_all_active_priced_variants_above_market_is_above_observed(market_context):
    db, service, _, product, _ = market_context
    add_variant(db, product.id, "above-a", "549")
    add_variant(db, product.id, "above-b", "599")
    add_evidence(service, product.id, "399")
    add_evidence(service, product.id, "499")
    analysis = service.get_market_evidence(product.id).analysis
    assert analysis.status == "MARKET_ABOVE_OBSERVED"
    assert analysis.evaluated_variant_count == 2
    assert analysis.letrusto_variant_min_price_inr == Decimal("549.00")
    assert analysis.letrusto_variant_max_price_inr == Decimal("599.00")


def test_mixed_variant_prices_are_conservatively_competitive(market_context):
    db, service, _, product, _ = market_context
    add_variant(db, product.id, "within", "449")
    add_variant(db, product.id, "above", "599")
    add_evidence(service, product.id, "399")
    add_evidence(service, product.id, "499")
    analysis = service.get_market_evidence(product.id).analysis
    assert analysis.status == "MARKET_COMPETITIVE"
    assert analysis.stored_product_selling_price_inr == Decimal("519.00")


def test_inactive_and_unpriced_variants_are_not_evaluated(market_context):
    db, service, _, product, _ = market_context
    add_variant(db, product.id, "active-priced", "449")
    add_variant(db, product.id, "inactive", "999", active=False)
    add_variant(db, product.id, "unpriced", None)
    add_evidence(service, product.id, "399")
    add_evidence(service, product.id, "499")
    analysis = service.get_market_evidence(product.id).analysis
    assert analysis.evaluated_variant_count == 1
    assert analysis.letrusto_variant_min_price_inr == Decimal("449.00")
    assert analysis.letrusto_variant_max_price_inr == Decimal("449.00")


def test_market_evidence_routes_require_authentication(market_context):
    _, _, _, product, _ = market_context
    app.dependency_overrides.clear()
    client = TestClient(app)
    assert client.post(f"/api/v1/admin/products/{product.id}/market-evidence", json=payload()).status_code == 401
    assert client.get(f"/api/v1/admin/products/{product.id}/market-evidence").status_code == 401
    assert client.delete(f"/api/v1/admin/products/{product.id}/market-evidence/{uuid4()}").status_code == 401


def test_evidence_preserves_product_state_and_cascades_on_product_delete(market_context):
    db, service, _, product, _ = market_context
    original = (
        product.status, product.commercial_status, product.cj_inventory, product.factory_inventory,
        product.supplier_cost, product.shipping_cost, product.selling_price,
    )
    evidence = add_evidence(service, product.id)
    stored = db.get(Product, product.id)
    assert (
        stored.status, stored.commercial_status, stored.cj_inventory, stored.factory_inventory,
        stored.supplier_cost, stored.shipping_cost, stored.selling_price,
    ) == original
    db.delete(stored)
    db.commit()
    assert db.get(ProductMarketEvidence, evidence.id) is None
