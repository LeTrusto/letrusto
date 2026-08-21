import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api.deps import get_admin_product_service, get_current_admin
from app.core.exceptions import BadRequestError, NotFoundError
from app.db.session import SessionLocal
from app.main import app
from app.models.entities import Product, SupplierCandidate, User
from app.schemas.admin_products import BulkApprovedProductImportRequest, SupplierCandidateCreate
from app.services.admin_product_service import AdminProductService
from app.services.catalog_enrichment_service import CatalogEnrichmentService
from app.services.supplier_candidate_readiness_service import SupplierCandidateReadinessService
from app.suppliers.base import RawSupplierProduct, RawVariant, ShippingOption, ShippingResult, ShippingValidation


class CandidateAdapter:
    supplier_name = "cj"

    def __init__(self, canonical_id: str, *, authenticated: bool = True, found: bool = True) -> None:
        self.canonical_id = canonical_id
        self.authenticated = authenticated
        self.found = found
        self.detail_calls: list[str] = []
        self.shipping_calls: list[tuple] = []

    async def authenticate(self) -> bool:
        return self.authenticated

    async def get_product(self, product_id: str) -> RawSupplierProduct | None:
        self.detail_calls.append(product_id)
        if not self.found:
            return None
        resolved_id = product_id if product_id.startswith("CAND-") else self.canonical_id
        return RawSupplierProduct(
            supplier_id="cj",
            supplier_product_id=resolved_id,
            supplier_sku=f"SKU-{resolved_id}",
            title=f"Candidate {resolved_id}",
            description="Verified candidate detail",
            images=["https://example.com/candidate.jpg"],
            category_name="Accessories",
            price_usd=2.0,
            weight_grams=20.0,
            variants=[RawVariant(
                supplier_variant_id=f"VID-{self.canonical_id}",
                supplier_variant_sku=f"VSKU-{self.canonical_id}",
                name="Default",
                option_key="Default",
                price_usd=2.0,
                weight_grams=20.0,
                total_inventory=1050,
                cj_inventory=50,
                factory_inventory=1000,
                inventory_verification="verified",
            )],
            inventory_total=50,
            total_inventory=1050,
            cj_inventory=50,
            factory_inventory=1000,
            inventory_verification="verified",
            warehouse_country="CN",
        )

    async def calculate_shipping(self, *args, **kwargs) -> ShippingResult:
        self.shipping_calls.append((args, kwargs))
        return ShippingResult(
            can_ship=True,
            validation=ShippingValidation.VERIFIED,
            options=[ShippingOption(carrier="Test", method="Test", cost_usd=2.0, estimated_days="10-15")],
            origin_country="CN",
            destination_country="IN",
        )


@pytest.fixture
def candidate_context(monkeypatch):
    import app.services.admin_product_service as service_module

    suffix = str(uuid4())[:8]
    canonical_id = f"CAND-{suffix}"
    adapter = CandidateAdapter(canonical_id)
    monkeypatch.setattr(service_module, "build_supplier_adapter", lambda *_: adapter)
    db = SessionLocal()
    admin = User(
        id=uuid4(),
        email=f"phase37b-{suffix}@example.com",
        full_name="Phase 3.7B Admin",
        role="admin",
    )
    db.add(admin)
    db.commit()
    service = AdminProductService(db)
    app.dependency_overrides[get_current_admin] = lambda: admin
    app.dependency_overrides[get_admin_product_service] = lambda: service
    yield db, service, TestClient(app), admin, adapter, canonical_id
    app.dependency_overrides.clear()
    db.rollback()
    candidate_ids = list(db.scalars(select(SupplierCandidate.id).where(SupplierCandidate.supplier_product_id.like(f"%{suffix}%"))))
    for candidate_id in candidate_ids:
        candidate = db.get(SupplierCandidate, candidate_id)
        if candidate:
            db.delete(candidate)
    products = list(db.scalars(select(Product).where(Product.supplier_product_id.like(f"%{suffix}%"))))
    for product in products:
        db.delete(product)
    db.commit()
    stored_admin = db.get(User, admin.id)
    if stored_admin:
        db.delete(stored_admin)
        db.commit()
    db.close()


def create_candidate(service, requested_id="REQUEST-SKU"):
    candidate = asyncio.run(service.create_supplier_candidate(
        SupplierCandidateCreate(supplier="cj", supplier_product_id=requested_id)
    ))
    stored = service.db.get(SupplierCandidate, candidate.id)
    snapshot = dict(stored.data_snapshot or {})
    reference = dict(snapshot.get("reference_data") or {})
    reference.setdefault("description", "Verified candidate detail")
    snapshot["reference_data"] = reference
    stored.data_snapshot = snapshot
    service.db.commit()
    return asyncio.run(CatalogEnrichmentService(service.db).enrich(candidate.id))


def approve_candidate(service, candidate_id, admin):
    return service.approve_supplier_candidate(candidate_id, admin)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("DISCOVERED", "VALIDATED"),
        ("DISCOVERED", "REVIEW"),
        ("DISCOVERED", "REJECTED"),
        ("REVIEW", "VALIDATED"),
        ("REVIEW", "REJECTED"),
    ],
)
def test_readiness_state_machine_allows_required_transitions(current, target):
    assert SupplierCandidateReadinessService.transition(current, target) == target


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("VALIDATED", "DISCOVERED"),
        ("VALIDATED", "REVIEW"),
        ("VALIDATED", "REJECTED"),
        ("REVIEW", "DISCOVERED"),
        ("REJECTED", "DISCOVERED"),
        ("REJECTED", "REVIEW"),
        ("REJECTED", "VALIDATED"),
        ("UNKNOWN", "REVIEW"),
    ],
)
def test_readiness_state_machine_rejects_invalid_transitions(current, target):
    with pytest.raises(BadRequestError, match="readiness"):
        SupplierCandidateReadinessService.transition(current, target)


def test_rejected_readiness_cannot_bypass_state_machine_or_approval(candidate_context):
    db, service, _, admin, _, _ = candidate_context
    candidate = create_candidate(service)
    stored = db.get(SupplierCandidate, candidate.id)
    stored.readiness_status = "REJECTED"
    db.commit()

    with pytest.raises(BadRequestError, match="readiness"):
        service.transition_supplier_candidate_readiness(candidate.id, "VALIDATED")
    with pytest.raises(BadRequestError, match="readiness"):
        service.approve_supplier_candidate(candidate.id, admin)


def test_rejected_approval_status_cannot_be_enriched(candidate_context):
    db, service, _, _, _, _ = candidate_context
    candidate = create_candidate(service)
    stored = db.get(SupplierCandidate, candidate.id)
    stored.approval_status = "REJECTED"
    db.commit()

    with pytest.raises(BadRequestError, match="Rejected"):
        asyncio.run(CatalogEnrichmentService(db).enrich(candidate.id))


def test_failed_enrichment_cannot_be_approved_or_imported(candidate_context):
    db, service, _, admin, _, _ = candidate_context
    candidate = create_candidate(service)
    stored = db.get(SupplierCandidate, candidate.id)
    stored.data_snapshot = {
        **stored.data_snapshot,
        "enrichment": {"status": "FAILED", "failure_reasons": ["AI_FAILURE"]},
    }
    db.commit()

    with pytest.raises(BadRequestError, match="successful enrichment"):
        service.approve_supplier_candidate(candidate.id, admin)

    stored.approval_status = "APPROVED"
    db.commit()
    result = asyncio.run(service.bulk_import_approved(BulkApprovedProductImportRequest(
        supplier="cj", product_ids=[candidate.supplier_product_id]
    )))
    assert result.results[0].status == "REJECTED_NOT_APPROVED"


def test_creation_resolves_and_persists_canonical_identity(candidate_context):
    db, service, _, _, _, canonical_id = candidate_context
    result = create_candidate(service)
    stored = db.get(SupplierCandidate, result.id)
    assert result.supplier_product_id == canonical_id
    assert result.supplier_sku == f"SKU-{canonical_id}"
    assert stored.name == f"Candidate {canonical_id}"


def test_creation_uses_one_detail_and_one_shipping_call(candidate_context):
    _, service, _, _, adapter, _ = candidate_context
    create_candidate(service)
    assert adapter.detail_calls == ["REQUEST-SKU"]
    assert len(adapter.shipping_calls) == 1


def test_creation_starts_in_required_review_states(candidate_context):
    _, service, _, _, _, _ = candidate_context
    result = create_candidate(service)
    assert (result.approval_status, result.commercial_status, result.market_status) == (
        "REVIEW", "REVIEW", "NOT_EVALUATED"
    )


def test_creation_persists_actual_validation_result(candidate_context):
    _, service, _, _, _, _ = candidate_context
    result = create_candidate(service)
    assert result.supplier_validation_status in {"PASS", "REVIEW", "REJECT"}
    assert isinstance(result.supplier_validation_score, int)


def test_creation_persists_candidate_review_snapshot(candidate_context):
    _, service, _, _, _, _ = candidate_context
    result = create_candidate(service)
    assert result.variants[0].supplier_variant_sku.startswith("VSKU-")
    assert result.variants[0].supplier_cost_usd == Decimal("2.0")
    assert result.variants[0].weight_grams == Decimal("20.0")
    assert result.variants[0].cj_inventory == 50
    assert result.variants[0].factory_inventory == 1000
    assert result.main_image == "https://example.com/candidate.jpg"
    assert result.target_margin_percent is not None
    assert result.snapshot_status == "AVAILABLE"


def test_legacy_candidate_without_snapshot_is_explicitly_unavailable(candidate_context):
    db, service, _, _, _, _ = candidate_context
    candidate = create_candidate(service)
    stored = db.get(SupplierCandidate, candidate.id)
    stored.data_snapshot = None
    stored.snapshot_status = "LEGACY_SNAPSHOT_UNAVAILABLE"
    db.commit()
    result = service.get_supplier_candidate(candidate.id)
    assert result.snapshot_status == "LEGACY_SNAPSHOT_UNAVAILABLE"
    assert result.variants == []
    assert result.discovery_min_selling_price_inr == candidate.discovery_min_selling_price_inr


def test_creation_does_not_create_product(candidate_context):
    db, service, _, _, _, canonical_id = candidate_context
    create_candidate(service)
    assert db.scalar(select(func.count(Product.id)).where(Product.supplier_product_id == canonical_id)) == 0


def test_candidate_model_has_no_cost_or_payload_columns():
    columns = set(SupplierCandidate.__table__.columns.keys())
    assert not columns.intersection({"supplier_cost", "shipping_cost", "economics", "images", "variants", "raw_payload"})


def test_duplicate_canonical_creation_is_idempotent(candidate_context):
    db, service, _, _, adapter, canonical_id = candidate_context
    first = create_candidate(service, "SKU-FIRST")
    second = create_candidate(service, "SKU-SECOND")
    assert first.id == second.id
    assert adapter.detail_calls == ["SKU-FIRST", "SKU-SECOND"]
    assert db.scalar(select(func.count(SupplierCandidate.id)).where(SupplierCandidate.supplier_product_id == canonical_id)) == 1


def test_creation_rejects_supplier_authentication_failure(candidate_context):
    _, service, _, _, adapter, _ = candidate_context
    adapter.authenticated = False
    with pytest.raises(BadRequestError, match="authentication"):
        create_candidate(service)


def test_creation_rejects_missing_supplier_product(candidate_context):
    _, service, _, _, adapter, _ = candidate_context
    adapter.found = False
    with pytest.raises(NotFoundError, match="not found"):
        create_candidate(service)


def test_list_is_newest_first(candidate_context):
    db, service, _, _, adapter, canonical_id = candidate_context
    first = create_candidate(service)
    adapter.canonical_id = f"{canonical_id}-NEW"
    second = create_candidate(service, "SECOND")
    db.get(SupplierCandidate, first.id).created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    db.get(SupplierCandidate, second.id).created_at = datetime(2026, 1, 2, tzinfo=timezone.utc)
    db.commit()
    candidate_rows = [
        item for item in service.list_supplier_candidates().candidates
        if item.supplier_product_id.startswith(canonical_id)
    ]
    assert [item.id for item in candidate_rows] == [second.id, first.id]


def test_approve_records_explicit_admin_identity(candidate_context):
    _, service, _, admin, _, _ = candidate_context
    candidate = create_candidate(service)
    result = approve_candidate(service, candidate.id, admin)
    assert result.approval_status == "APPROVED"
    assert result.commercial_status == "APPROVED"
    assert result.approved_by_user_id == admin.id
    assert result.approved_at is not None


def test_rejected_candidate_can_be_reapproved(candidate_context):
    _, service, _, admin, _, _ = candidate_context
    candidate = create_candidate(service)
    service.reject_supplier_candidate(candidate.id)
    assert approve_candidate(service, candidate.id, admin).approval_status == "APPROVED"


def test_repeated_approval_is_idempotent(candidate_context):
    _, service, _, admin, _, _ = candidate_context
    candidate = create_candidate(service)
    first = approve_candidate(service, candidate.id, admin)
    second = approve_candidate(service, candidate.id, admin)
    assert second.approved_at == first.approved_at


def test_reject_clears_approval_metadata(candidate_context):
    _, service, _, admin, _, _ = candidate_context
    candidate = create_candidate(service)
    approve_candidate(service, candidate.id, admin)
    result = service.reject_supplier_candidate(candidate.id)
    assert result.approval_status == "REJECTED"
    assert result.commercial_status == "REJECTED"
    assert result.approved_at is None
    assert result.approved_by_user_id is None


def test_rejection_api_requires_reason_and_persists_decision_audit(candidate_context):
    db, service, client, _, _, _ = candidate_context
    candidate = create_candidate(service)
    assert client.post(f"/api/v1/admin/supplier-candidates/{candidate.id}/reject", json={}).status_code == 422
    response = client.post(
        f"/api/v1/admin/supplier-candidates/{candidate.id}/reject",
        json={"reason": "Insufficient market evidence"},
    )
    assert response.status_code == 200
    stored = db.get(SupplierCandidate, candidate.id)
    assert stored.rejection_reason == "Insufficient market evidence"
    assert stored.decision_at is not None
    assert stored.decision_by_user_id is not None


def test_supplier_validation_reject_cannot_be_approved(candidate_context):
    db, service, _, admin, _, _ = candidate_context
    candidate = create_candidate(service)
    stored = db.get(SupplierCandidate, candidate.id)
    stored.supplier_validation_status = "REJECT"
    db.commit()

    with pytest.raises(BadRequestError, match="supplier validation"):
        approve_candidate(service, candidate.id, admin)

    db.refresh(stored)
    assert stored.approval_status == "REVIEW"
    assert stored.commercial_status == "REVIEW"


@pytest.mark.parametrize("action", ["approve", "reject"])
def test_imported_candidate_decision_is_blocked(candidate_context, action):
    db, service, _, admin, _, _ = candidate_context
    candidate = create_candidate(service)
    stored = db.get(SupplierCandidate, candidate.id)
    stored.approval_status = "IMPORTED"
    db.commit()
    with pytest.raises(BadRequestError, match="Imported"):
        if action == "approve":
            service.approve_supplier_candidate(candidate.id, admin)
        else:
            service.reject_supplier_candidate(candidate.id)


@pytest.mark.parametrize("method,path", [
    ("post", "/api/v1/admin/supplier-candidates"),
    ("get", "/api/v1/admin/supplier-candidates"),
    ("post", f"/api/v1/admin/supplier-candidates/{uuid4()}/approve"),
    ("post", f"/api/v1/admin/supplier-candidates/{uuid4()}/reject"),
    ("post", "/api/v1/admin/products/bulk-import"),
])
def test_candidate_routes_require_admin_authentication(method, path):
    client = TestClient(app)
    payload = {"supplier": "cj", "supplier_product_id": "X"} if path.endswith("supplier-candidates") and method == "post" else {"supplier": "cj", "product_ids": ["X"]}
    response = client.post(path, json=payload) if method == "post" else client.get(path)
    assert response.status_code == 401


@pytest.mark.parametrize("payload", [
    {"supplier": "cj", "supplier_product_id": ""},
    {"supplier": "cj", "supplier_product_id": "   "},
    {"supplier": "other", "supplier_product_id": "X"},
    {"supplier": "cj", "supplier_product_id": "X", "destination": "US"},
])
def test_candidate_request_validation(candidate_context, payload):
    _, _, client, _, _, _ = candidate_context
    assert client.post("/api/v1/admin/supplier-candidates", json=payload).status_code == 422


def test_bulk_rejects_missing_candidate(candidate_context):
    _, service, _, _, _, _ = candidate_context
    result = asyncio.run(service.bulk_import_approved(BulkApprovedProductImportRequest(supplier="cj", product_ids=["MISSING"])))
    assert result.results[0].status == "REJECTED_NOT_APPROVED"


@pytest.mark.parametrize("approval_status", ["REVIEW", "REJECTED"])
def test_bulk_rejects_unapproved_candidate(candidate_context, approval_status):
    db, service, _, _, _, _ = candidate_context
    candidate = create_candidate(service)
    db.get(SupplierCandidate, candidate.id).approval_status = approval_status
    db.commit()
    result = asyncio.run(service.bulk_import_approved(BulkApprovedProductImportRequest(supplier="cj", product_ids=[candidate.supplier_product_id])))
    assert result.results[0].status == "REJECTED_NOT_APPROVED"


def test_bulk_rejects_candidate_with_rejected_readiness_even_if_approved(candidate_context):
    db, service, _, _, _, _ = candidate_context
    candidate = create_candidate(service)
    stored = db.get(SupplierCandidate, candidate.id)
    stored.approval_status = "APPROVED"
    stored.readiness_status = "REJECTED"
    db.commit()
    result = asyncio.run(service.bulk_import_approved(BulkApprovedProductImportRequest(supplier="cj", product_ids=[candidate.supplier_product_id])))
    assert result.results[0].status == "REJECTED_NOT_APPROVED"


def test_bulk_reports_already_imported(candidate_context):
    db, service, _, _, _, _ = candidate_context
    candidate = create_candidate(service)
    stored = db.get(SupplierCandidate, candidate.id)
    stored.approval_status = "IMPORTED"
    db.commit()
    result = asyncio.run(service.bulk_import_approved(BulkApprovedProductImportRequest(supplier="cj", product_ids=[candidate.supplier_product_id])))
    assert result.already_imported_count == 1
    assert result.results[0].status == "ALREADY_IMPORTED"


def test_bulk_imports_approved_candidate_as_draft(candidate_context):
    db, service, _, admin, _, _ = candidate_context
    candidate = approve_candidate(service, create_candidate(service).id, admin)
    result = asyncio.run(service.bulk_import_approved(BulkApprovedProductImportRequest(supplier="cj", product_ids=[candidate.supplier_product_id])))
    product = db.get(Product, result.results[0].product_id)
    assert result.results[0].status == "IMPORTED"
    assert product.status == "DRAFT"
    assert product.commercial_status == "APPROVED"
    stored = db.get(SupplierCandidate, candidate.id)
    assert stored.imported_at is not None
    assert stored.import_result == "IMPORTED"


@pytest.mark.parametrize("approval_status", ["REVIEW", "REJECTED", "APPROVED", "IMPORTED"])
def test_legacy_candidate_decision_and_import_state_remain_unchanged(candidate_context, approval_status):
    db, service, _, admin, _, _ = candidate_context
    candidate = create_candidate(service)
    stored = db.get(SupplierCandidate, candidate.id)
    stored.data_snapshot = None
    stored.snapshot_status = "LEGACY_SNAPSHOT_UNAVAILABLE"
    stored.approval_status = approval_status
    db.commit()
    result = service.get_supplier_candidate(candidate.id)
    assert result.snapshot_status == "LEGACY_SNAPSHOT_UNAVAILABLE"
    assert result.variants == []
    assert result.approval_status == approval_status


def test_bulk_resolves_unique_candidate_sku(candidate_context):
    _, service, _, admin, _, _ = candidate_context
    candidate = approve_candidate(service, create_candidate(service).id, admin)
    result = asyncio.run(service.bulk_import_approved(BulkApprovedProductImportRequest(supplier="cj", product_ids=[candidate.supplier_sku])))
    assert result.results[0].canonical_supplier_product_id == candidate.supplier_product_id
    assert result.results[0].status == "IMPORTED"


def test_bulk_duplicate_request_becomes_already_imported(candidate_context):
    _, service, _, admin, _, _ = candidate_context
    candidate = approve_candidate(service, create_candidate(service).id, admin)
    result = asyncio.run(service.bulk_import_approved(BulkApprovedProductImportRequest(
        supplier="cj", product_ids=[candidate.supplier_product_id, candidate.supplier_product_id]
    )))
    assert [item.status for item in result.results] == ["IMPORTED", "ALREADY_IMPORTED"]


def test_bulk_links_existing_product_without_mutating_it(candidate_context):
    db, service, _, admin, _, canonical_id = candidate_context
    candidate = approve_candidate(service, create_candidate(service).id, admin)
    existing = Product(
        id=uuid4(), slug=f"existing-{canonical_id.lower()}", name="Existing", description="Preserve",
        status="PAUSED", supplier="cj", supplier_product_id=canonical_id,
        supplier_cost=Decimal("12.34"), commercial_status="REJECTED",
    )
    db.add(existing)
    db.commit()
    result = asyncio.run(service.bulk_import_approved(BulkApprovedProductImportRequest(supplier="cj", product_ids=[canonical_id])))
    db.refresh(existing)
    assert result.results[0].status == "ALREADY_EXISTS"
    assert (existing.status, existing.commercial_status, existing.supplier_cost) == ("PAUSED", "REJECTED", Decimal("12.34"))
    assert db.get(SupplierCandidate, candidate.id).imported_product_id == existing.id


def test_bulk_copies_candidate_approval_audit(candidate_context):
    db, service, _, admin, _, _ = candidate_context
    candidate = approve_candidate(service, create_candidate(service).id, admin)
    result = asyncio.run(service.bulk_import_approved(BulkApprovedProductImportRequest(supplier="cj", product_ids=[candidate.supplier_product_id])))
    product = db.get(Product, result.results[0].product_id)
    assert product.approval_decided_at == candidate.approved_at
    assert product.approval_decided_by_user_id == admin.id
    assert product.approval_evidence["source"] == "SUPPLIER_CANDIDATE_APPROVAL"
    assert product.approval_evidence["supplier_candidate_id"] == str(candidate.id)
    assert product.approval_evidence["market_status"] == "NOT_EVALUATED"


def test_bulk_preserves_single_import_supplier_data(candidate_context):
    db, service, _, admin, _, canonical_id = candidate_context
    candidate = approve_candidate(service, create_candidate(service).id, admin)
    result = asyncio.run(service.bulk_import_approved(BulkApprovedProductImportRequest(supplier="cj", product_ids=[canonical_id])))
    product = db.get(Product, result.results[0].product_id)
    assert product.supplier_product_id == canonical_id
    assert product.cj_inventory == 50
    assert product.factory_inventory == 1000
    assert product.total_inventory == 1050
    assert len(product.images) == 1
    assert product.variants[0].supplier_variant_sku == f"VSKU-{canonical_id}"


def test_bulk_failure_does_not_undo_prior_success(candidate_context, monkeypatch):
    db, service, _, admin, adapter, canonical_id = candidate_context
    first = approve_candidate(service, create_candidate(service).id, admin)
    adapter.canonical_id = f"{canonical_id}-FAIL"
    second = approve_candidate(service, create_candidate(service, "FAIL").id, admin)
    original = AdminProductService.import_product

    async def fail_second(self, payload, *, commit=True):
        if payload.supplier_product_id == second.supplier_product_id:
            raise RuntimeError("isolated failure")
        return await original(self, payload, commit=commit)

    monkeypatch.setattr(AdminProductService, "import_product", fail_second)
    result = asyncio.run(service.bulk_import_approved(BulkApprovedProductImportRequest(
        supplier="cj", product_ids=[first.supplier_product_id, second.supplier_product_id]
    )))
    assert [item.status for item in result.results] == ["IMPORTED", "FAILED"]
    assert db.scalar(select(func.count(Product.id)).where(Product.supplier_product_id == first.supplier_product_id)) == 1
    assert db.scalar(select(func.count(Product.id)).where(Product.supplier_product_id == second.supplier_product_id)) == 0
    db.refresh(db.get(SupplierCandidate, second.id))
    assert db.get(SupplierCandidate, second.id).approval_status == "APPROVED"
