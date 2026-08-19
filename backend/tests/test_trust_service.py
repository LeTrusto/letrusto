from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from app.api.deps import get_db
from app.core.security import create_access_token
from app.core.exceptions import BadRequestError, NotFoundError
from app.db.session import SessionLocal
from app.main import app
from app.models.entities import Product, ProductVariant, TrustAuditEvent, TrustClaim, TrustClaimEvidence, TrustEvidence, TrustVerification, User
from app.schemas.trust import TrustClaimCreate, TrustClaimEvidenceCreate, TrustClaimUpdate, TrustEvidenceCreate, TrustEvidenceUpdate, TrustVerificationCreate
from app.services.trust_service import TrustService


@pytest.fixture
def trust_context():
    db = SessionLocal()
    suffix = uuid4().hex[:8]
    admin = User(email=f"trust-admin-{suffix}@example.com", full_name="Trust Admin", role="admin")
    customer = User(email=f"trust-customer-{suffix}@example.com", full_name="Trust Customer")
    product = Product(
        slug=f"trust-product-{suffix}", name="Trust Product", description="Test product", status="ACTIVE",
        supplier="cj", supplier_product_id=f"CJ-TRUST-{suffix}", price_value=Decimal("100"), selling_price=Decimal("100"),
        ai_score=1, rating=Decimal("1"), ai_summary="", review_summary="",
    )
    variant = ProductVariant(product=product, supplier_variant_id=f"VID-{suffix}", supplier_variant_sku=f"SKU-{suffix}", name="Default", position=1, selling_price=Decimal("100"), cj_inventory=5, active=True)
    db.add_all([admin, customer, product, variant])
    db.commit()
    db.execute(text("SELECT set_config('letrusto.trust_history_maintenance', 'off', false)"))
    db.commit()
    yield db, admin, customer, product
    db.execute(text("SELECT set_config('letrusto.trust_history_maintenance', 'on', false)"))
    claim_ids = list(db.scalars(select(TrustClaim.id).where(TrustClaim.product_id == product.id)))
    if claim_ids:
        db.query(TrustAuditEvent).filter(TrustAuditEvent.claim_id.in_(claim_ids)).delete(synchronize_session=False)
        db.query(TrustVerification).filter(TrustVerification.claim_id.in_(claim_ids)).delete(synchronize_session=False)
        db.query(TrustClaimEvidence).filter(TrustClaimEvidence.claim_id.in_(claim_ids)).delete(synchronize_session=False)
        db.query(TrustClaim).filter(TrustClaim.id.in_(claim_ids)).delete(synchronize_session=False)
    db.query(TrustEvidence).filter(TrustEvidence.created_by_user_id == admin.id).delete(synchronize_session=False)
    db.delete(product)
    db.delete(admin)
    db.delete(customer)
    db.commit()
    db.execute(text("SELECT set_config('letrusto.trust_history_maintenance', 'off', false)"))
    db.commit()
    db.close()


def claim_payload(product_id):
    return TrustClaimCreate(product_id=product_id, claim_type="MATERIAL", claim_value="Stainless Steel", source="SUPPLIER_DECLARATION")


def evidence_payload(suffix: str):
    return TrustEvidenceCreate(evidence_type="SUPPLIER_DOCUMENT", title=f"Trust evidence {suffix}", reference_url="https://example.com/specification.pdf", source="SUPPLIER")


def test_claim_evidence_verification_history_and_audit(trust_context):
    db, admin, _, product = trust_context
    service = TrustService(db)
    claim = service.create_claim(claim_payload(product.id), admin)
    evidence_one = service.create_evidence(evidence_payload(product.slug[-8:]), admin)
    evidence_two = service.create_evidence(TrustEvidenceCreate(evidence_type="TEST_REPORT", title=f"Trust evidence {product.slug[-8:]} two", storage_reference="trust/test-report.pdf"), admin)
    service.attach_evidence(claim.id, TrustClaimEvidenceCreate(evidence_id=evidence_one.id), admin)
    service.attach_evidence(claim.id, TrustClaimEvidenceCreate(evidence_id=evidence_two.id, assessment_metadata={"relevance": "primary"}), admin)
    pending = service.create_verification(claim.id, TrustVerificationCreate(verification_status="PENDING", verification_method="INTERNAL_REVIEW", evidence_ids=[evidence_one.id]), admin)
    verified = service.create_verification(claim.id, TrustVerificationCreate(verification_status="VERIFIED", verification_method="TEST_REPORT", evidence_ids=[evidence_one.id, evidence_two.id], notes="Document reviewed"), admin)
    detail = service.get_claim(claim.id)
    assert detail.verification_status == "VERIFIED"
    assert len(detail.evidence_links) == 2
    assert [item.id for item in service.verification_history(claim.id)] == [verified.id, pending.id]
    assert verified.evidence_snapshot and len(verified.evidence_snapshot) == 2
    audit = service.audit_history(claim.id)
    assert {item.event_type for item in audit} >= {"CLAIM_CREATED", "EVIDENCE_ATTACHED", "VERIFICATION_CREATED"}
    assert all(item.actor_user_id == admin.id and item.created_at for item in audit)


def test_verified_claim_cannot_change_and_verification_snapshot_survives_evidence_update(trust_context):
    db, admin, _, product = trust_context
    service = TrustService(db)
    claim = service.create_claim(claim_payload(product.id), admin)
    evidence = service.create_evidence(evidence_payload(product.slug[-8:]), admin)
    service.attach_evidence(claim.id, TrustClaimEvidenceCreate(evidence_id=evidence.id), admin)
    verification = service.create_verification(claim.id, TrustVerificationCreate(verification_status="VERIFIED", verification_method="SUPPLIER_DOCUMENT", evidence_ids=[evidence.id]), admin)
    original_snapshot = verification.evidence_snapshot
    with pytest.raises(BadRequestError, match="Verified trust claims"):
        service.update_claim(claim.id, TrustClaimUpdate(claim_value="Changed material"), admin)
    service.update_evidence(evidence.id, TrustEvidenceUpdate(title="Updated supplier document"), admin)
    history = service.verification_history(claim.id)
    assert history[0].evidence_snapshot == original_snapshot


def test_verification_and_audit_rows_are_database_immutable(trust_context):
    db, admin, _, product = trust_context
    service = TrustService(db)
    claim = service.create_claim(claim_payload(product.id), admin)
    evidence = service.create_evidence(evidence_payload(product.slug[-8:]), admin)
    service.attach_evidence(claim.id, TrustClaimEvidenceCreate(evidence_id=evidence.id), admin)
    verification = service.create_verification(claim.id, TrustVerificationCreate(verification_status="PENDING", verification_method="INTERNAL_REVIEW", evidence_ids=[evidence.id]), admin)
    stored_verification = db.get(TrustVerification, verification.id)
    stored_verification.notes = "Tampered"
    with pytest.raises(Exception, match="append-only"):
        db.commit()
    db.rollback()
    audit = db.scalar(select(TrustAuditEvent).where(TrustAuditEvent.claim_id == claim.id))
    audit.reason = "Tampered"
    with pytest.raises(Exception, match="append-only"):
        db.commit()
    db.rollback()


def test_attached_evidence_cannot_be_deleted_and_service_rechecks_status(trust_context):
    db, admin, _, product = trust_context
    service = TrustService(db)
    claim = service.create_claim(claim_payload(product.id), admin)
    evidence = service.create_evidence(evidence_payload(product.slug[-8:]), admin)
    service.attach_evidence(claim.id, TrustClaimEvidenceCreate(evidence_id=evidence.id), admin)
    with pytest.raises(BadRequestError, match="invalid trust verification status"):
        service.create_verification(
            claim.id,
            SimpleNamespace(
                verification_status="INVALID",
                verification_method="SUPPLIER_DOCUMENT",
                evidence_ids=[evidence.id],
                notes=None,
                verification_metadata=None,
                expires_at=None,
            ),
            admin,
        )
    db.delete(db.get(TrustEvidence, evidence.id))
    with pytest.raises(Exception):
        db.commit()
    db.rollback()
    service.create_verification(claim.id, TrustVerificationCreate(verification_status="PENDING", verification_method="INTERNAL_REVIEW", evidence_ids=[evidence.id]), admin)
    db.delete(db.get(TrustClaim, claim.id))
    with pytest.raises(Exception, match="append-only"):
        db.commit()
    db.rollback()


def test_claim_update_and_expiry_preserve_history(trust_context):
    db, admin, _, product = trust_context
    service = TrustService(db)
    claim = service.create_claim(claim_payload(product.id), admin)
    evidence = service.create_evidence(evidence_payload(product.slug[-8:]), admin)
    service.attach_evidence(claim.id, TrustClaimEvidenceCreate(evidence_id=evidence.id), admin)
    updated = service.update_claim(claim.id, TrustClaimUpdate(claim_description="Nickel-free steel"), admin)
    assert updated.claim_description == "Nickel-free steel"
    service.create_verification(claim.id, TrustVerificationCreate(verification_status="VERIFIED", verification_method="SUPPLIER_DOCUMENT", evidence_ids=[evidence.id], expires_at=datetime.now(timezone.utc) - timedelta(days=1)), admin)
    detail = service.get_claim(claim.id)
    assert detail.verification_status == "EXPIRED"
    assert len(detail.verifications) == 1
    assert any(item.event_type == "CLAIM_EXPIRED" for item in detail.audit_events)


def test_invalid_product_relationship_and_status_are_rejected(trust_context):
    db, admin, _, product = trust_context
    service = TrustService(db)
    with pytest.raises(NotFoundError):
        service.create_claim(claim_payload(uuid4()), admin)
    claim = service.create_claim(claim_payload(product.id), admin)
    evidence = service.create_evidence(evidence_payload(product.slug[-8:]), admin)
    with pytest.raises(BadRequestError, match="require attached active evidence"):
        service.create_verification(claim.id, TrustVerificationCreate(verification_status="VERIFIED", verification_method="SUPPLIER_DOCUMENT"), admin)
    with pytest.raises(BadRequestError, match="attached"):
        service.create_verification(claim.id, TrustVerificationCreate(verification_status="VERIFIED", verification_method="SUPPLIER_DOCUMENT", evidence_ids=[evidence.id]), admin)
    with pytest.raises(Exception):
        TrustVerificationCreate(verification_status="INVALID", verification_method="SUPPLIER_DOCUMENT")
    with pytest.raises(Exception):
        TrustEvidenceCreate(evidence_type="SUPPLIER_DOCUMENT", title="Missing reference")


def test_evidence_can_be_deactivated_without_breaking_historical_link(trust_context):
    db, admin, _, product = trust_context
    service = TrustService(db)
    claim = service.create_claim(claim_payload(product.id), admin)
    evidence = service.create_evidence(evidence_payload(product.slug[-8:]), admin)
    link = service.attach_evidence(claim.id, TrustClaimEvidenceCreate(evidence_id=evidence.id), admin)
    service.update_evidence(evidence.id, TrustEvidenceUpdate(is_active=False), admin)
    detail = service.get_claim(claim.id)
    assert detail.evidence_links[0].id == link.id
    assert service.get_evidence(evidence.id).is_active is False
    assert any(item.event_type == "EVIDENCE_UPDATED" for item in detail.audit_events)


def test_trust_endpoints_are_admin_only(trust_context):
    db, admin, customer, product = trust_context
    app.dependency_overrides[get_db] = lambda: db
    try:
        client = TestClient(app)
        assert client.get(f"/api/v1/admin/trust/products/{product.id}/claims").status_code == 401
        customer_token = create_access_token(str(customer.id))
        assert client.get(f"/api/v1/admin/trust/products/{product.id}/claims", headers={"Authorization": f"Bearer {customer_token}"}).status_code == 401
        admin_token = create_access_token(str(admin.id))
        response = client.post("/api/v1/admin/trust/claims", json=claim_payload(product.id).model_dump(mode="json"), headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 201
    finally:
        app.dependency_overrides.clear()
