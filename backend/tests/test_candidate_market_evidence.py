from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import get_admin_product_service, get_current_admin
from app.db.session import SessionLocal
from app.main import app
from app.models.entities import Product, ProductMarketEvidence, SupplierCandidate
from app.services.admin_product_service import AdminProductService


@pytest.fixture
def candidate_evidence_context():
    db = SessionLocal()
    suffix = str(uuid4())[:8]
    candidate = SupplierCandidate(
        supplier="cj",
        supplier_product_id=f"candidate-evidence-{suffix}",
        name="Candidate evidence fixture",
        approval_status="REVIEW",
        commercial_status="REVIEW",
        market_status="NOT_EVALUATED",
        discovery_min_selling_price_inr=Decimal("450.00"),
        discovery_max_selling_price_inr=Decimal("550.00"),
    )
    other_candidate = SupplierCandidate(
        supplier="cj",
        supplier_product_id=f"candidate-evidence-other-{suffix}",
        name="Other candidate",
        approval_status="REVIEW",
        commercial_status="REVIEW",
        market_status="NOT_EVALUATED",
    )
    product = Product(
        slug=f"candidate-evidence-{suffix}",
        name="Unrelated product",
        description="Fixture only",
        status="DRAFT",
        commercial_status="REVIEW",
        selling_price=Decimal("999.00"),
    )
    db.add_all([candidate, other_candidate, product])
    db.commit()
    service = AdminProductService(db)
    app.dependency_overrides[get_current_admin] = lambda: object()
    app.dependency_overrides[get_admin_product_service] = lambda: service
    yield db, service, TestClient(app), candidate, other_candidate, product
    app.dependency_overrides.clear()
    db.rollback()
    for entity in (candidate, other_candidate, product):
        stored = db.get(type(entity), entity.id)
        if stored:
            db.delete(stored)
    db.commit()
    db.close()


def evidence_payload(price: str) -> dict[str, str]:
    return {
        "competitor_name": "Fixture competitor",
        "product_name": "Fixture listing",
        "source_url": "https://example.com/fixture",
        "observed_price_inr": price,
        "currency": "INR",
    }


def test_candidate_evidence_crud_statistics_and_status(candidate_evidence_context):
    db, _, client, candidate, _, _ = candidate_evidence_context
    first = client.post(
        f"/api/v1/admin/supplier-candidates/{candidate.id}/market-evidence",
        json=evidence_payload("399"),
    )
    assert first.status_code == 200
    assert first.json()["product_id"] is None
    assert first.json()["supplier_candidate_id"] == str(candidate.id)
    assert db.get(SupplierCandidate, candidate.id).market_status == "INSUFFICIENT_MARKET_DATA"

    second = client.post(
        f"/api/v1/admin/supplier-candidates/{candidate.id}/market-evidence",
        json=evidence_payload("499"),
    )
    response = client.get(f"/api/v1/admin/supplier-candidates/{candidate.id}/market-evidence")
    assert response.status_code == 200
    body = response.json()
    assert body["product_id"] is None
    assert body["supplier_candidate_id"] == str(candidate.id)
    assert body["analysis"]["observation_count"] == 2
    assert body["analysis"]["minimum_price_inr"] == "399.00"
    assert body["analysis"]["maximum_price_inr"] == "499.00"
    assert body["analysis"]["average_price_inr"] == "449.00"
    assert body["analysis"]["median_price_inr"] == "449.00"
    assert body["analysis"]["status"] == "MARKET_COMPETITIVE"
    assert db.get(SupplierCandidate, candidate.id).market_status == "MARKET_COMPETITIVE"

    assert client.delete(
        f"/api/v1/admin/supplier-candidates/{candidate.id}/market-evidence/{second.json()['id']}"
    ).status_code == 204
    assert db.get(SupplierCandidate, candidate.id).market_status == "INSUFFICIENT_MARKET_DATA"


def test_candidate_price_range_is_conservatively_compared(candidate_evidence_context):
    db, _, client, candidate, _, _ = candidate_evidence_context
    candidate.discovery_min_selling_price_inr = Decimal("600.00")
    candidate.discovery_max_selling_price_inr = Decimal("700.00")
    db.commit()
    for price in ("399", "499"):
        assert client.post(
            f"/api/v1/admin/supplier-candidates/{candidate.id}/market-evidence",
            json=evidence_payload(price),
        ).status_code == 200
    response = client.get(f"/api/v1/admin/supplier-candidates/{candidate.id}/market-evidence")
    assert response.json()["analysis"]["status"] == "MARKET_ABOVE_OBSERVED"
    assert db.get(SupplierCandidate, candidate.id).market_status == "MARKET_ABOVE_OBSERVED"


def test_candidate_without_discovery_prices_reports_evidence_available(candidate_evidence_context):
    db, _, client, candidate, _, _ = candidate_evidence_context
    candidate.discovery_min_selling_price_inr = None
    candidate.discovery_max_selling_price_inr = None
    db.commit()
    for price in ("399", "499"):
        client.post(
            f"/api/v1/admin/supplier-candidates/{candidate.id}/market-evidence",
            json=evidence_payload(price),
        )
    response = client.get(f"/api/v1/admin/supplier-candidates/{candidate.id}/market-evidence")
    assert response.json()["analysis"]["status"] == "MARKET_EVIDENCE_AVAILABLE"
    assert db.get(SupplierCandidate, candidate.id).market_status == "MARKET_EVIDENCE_AVAILABLE"


def test_candidate_evidence_ownership_is_enforced(candidate_evidence_context):
    db, _, client, candidate, other_candidate, product = candidate_evidence_context
    created = client.post(
        f"/api/v1/admin/supplier-candidates/{candidate.id}/market-evidence",
        json=evidence_payload("399"),
    ).json()
    evidence_id = created["id"]
    assert client.delete(
        f"/api/v1/admin/supplier-candidates/{other_candidate.id}/market-evidence/{evidence_id}"
    ).status_code == 404
    assert client.delete(
        f"/api/v1/admin/products/{product.id}/market-evidence/{evidence_id}"
    ).status_code == 404
    assert db.get(ProductMarketEvidence, evidence_id) is not None


def test_candidate_evidence_preserves_candidate_and_product_business_state(candidate_evidence_context):
    db, _, client, candidate, _, product = candidate_evidence_context
    candidate_state = (candidate.approval_status, candidate.commercial_status, candidate.approved_at)
    product_state = (product.status, product.commercial_status, product.selling_price)
    client.post(
        f"/api/v1/admin/supplier-candidates/{candidate.id}/market-evidence",
        json=evidence_payload("399"),
    )
    stored_candidate = db.get(SupplierCandidate, candidate.id)
    stored_product = db.get(Product, product.id)
    assert (stored_candidate.approval_status, stored_candidate.commercial_status, stored_candidate.approved_at) == candidate_state
    assert (stored_product.status, stored_product.commercial_status, stored_product.selling_price) == product_state


def test_candidate_delete_cascades_owned_evidence(candidate_evidence_context):
    db, _, client, candidate, _, _ = candidate_evidence_context
    evidence_id = client.post(
        f"/api/v1/admin/supplier-candidates/{candidate.id}/market-evidence",
        json=evidence_payload("399"),
    ).json()["id"]
    db.delete(db.get(SupplierCandidate, candidate.id))
    db.commit()
    assert db.get(ProductMarketEvidence, evidence_id) is None


@pytest.mark.parametrize("owner_mode", ["neither", "both"])
def test_market_evidence_requires_exactly_one_owner(candidate_evidence_context, owner_mode):
    db, _, _, candidate, _, product = candidate_evidence_context
    evidence = ProductMarketEvidence(
        product_id=product.id if owner_mode == "both" else None,
        supplier_candidate_id=candidate.id if owner_mode == "both" else None,
        competitor_name="Fixture competitor",
        product_name="Fixture listing",
        source_url="https://example.com/fixture",
        observed_price_inr=Decimal("399.00"),
        currency="INR",
    )
    db.add(evidence)
    with pytest.raises(SQLAlchemyError):
        db.commit()
    db.rollback()


def test_candidate_market_evidence_routes_require_authentication(candidate_evidence_context):
    _, _, _, candidate, _, _ = candidate_evidence_context
    app.dependency_overrides.clear()
    client = TestClient(app)
    base = f"/api/v1/admin/supplier-candidates/{candidate.id}/market-evidence"
    assert client.post(base, json=evidence_payload("399")).status_code == 401
    assert client.get(base).status_code == 401
    assert client.delete(f"{base}/{uuid4()}").status_code == 401