from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_admin_product_service, get_current_admin
from app.core.exceptions import BadRequestError
from app.db.session import SessionLocal
from app.main import app
from app.models.entities import Product, ProductImage, ProductMarketEvidence, ProductVariant, User
from app.schemas.admin_products import ProductRejectionRequest, ProductStatusUpdate
from app.services.admin_product_service import AdminProductService
from app.services.launch_pricing_policy import LaunchPricingPolicy
from app.services.pricing_engine import calculate_launch_variant_price


@pytest.fixture
def approval_context():
    db = SessionLocal()
    service = AdminProductService(db)
    admin = User(id=uuid4(), email=f"phase36-{uuid4()}@example.com", full_name="Phase 3.6 Admin", role="admin")
    product = Product(
        id=uuid4(), slug=f"phase36-{uuid4()}", name="Phase 3.6 product",
        description="Complete approval fixture", status="DRAFT", supplier="cj",
        supplier_product_id=f"phase36-{uuid4()}", supplier_cost=Decimal("91.02"),
        shipping_cost=Decimal("167.00"), selling_price=Decimal("519.00"),
        total_inventory=77691, cj_inventory=40, factory_inventory=77651,
        commercial_status="REVIEW",
        supplier_validation_status="REVIEW", supplier_validation_score=61,
        supplier_validation_notes=["Margin unknown - missing cost inputs"],
    )
    calculation = calculate_launch_variant_price(
        supplier_cost_usd=Decimal("1.09"), shipping_cost_inr=product.shipping_cost,
        policy=service.launch_pricing_policy,
    )
    db.add_all([admin, product])
    db.flush()
    image = ProductImage(product_id=product.id, url="https://cf.cjdropshipping.com/quick/product/phase36.jpg", position=1)
    variant = ProductVariant(
        product_id=product.id, supplier_variant_id="phase36-variant", supplier_variant_sku="phase36-sku",
        name="Default", attributes="Default", supplier_cost=Decimal("91.02"),
        supplier_cost_usd=Decimal("1.09"), selling_price=calculation.selling_price_inr,
        total_inventory=77691, cj_inventory=40, factory_inventory=77651, active=True, position=1,
    )
    db.add_all([image, variant])
    db.commit()
    app.dependency_overrides[get_current_admin] = lambda: admin
    app.dependency_overrides[get_admin_product_service] = lambda: service
    client = TestClient(app)
    yield db, service, client, admin, product, variant
    app.dependency_overrides.clear()
    db.rollback()
    stored = db.get(Product, product.id)
    if stored:
        db.delete(stored)
    stored_admin = db.get(User, admin.id)
    if stored_admin:
        db.delete(stored_admin)
    db.commit()
    db.close()


def immutable_state(product, variant):
    return (
        product.total_inventory, product.cj_inventory, product.factory_inventory,
        product.supplier_cost, product.shipping_cost, product.selling_price,
        variant.supplier_cost, variant.supplier_cost_usd, variant.selling_price,
        variant.total_inventory, variant.cj_inventory, variant.factory_inventory,
    )


def make_activation_ready(db, product):
    product.category_id = 25
    product.brand_id = 1
    product.supplier_validation_status = "PASS"
    product.last_supplier_sync_at = datetime.now(timezone.utc)
    db.commit()


def test_admin_can_approve_review_without_activation(approval_context):
    db, service, _, admin, product, _ = approval_context
    result = service.approve(product.id, admin)
    stored = db.get(Product, product.id)
    assert result.commercial_status == "APPROVED"
    assert result.status == "DRAFT"
    assert stored.approval_decided_by_user_id == admin.id
    assert stored.approval_decided_at is not None
    assert stored.approval_rejection_reason is None
    assert stored.approval_evidence["decision"] == "APPROVED"
    assert stored.approval_evidence["decided_by_user_id"] == str(admin.id)
    assert stored.approval_evidence["supplier_validation"] == {
        "status": "REVIEW", "score": 61, "validated_at": None,
    }
    assert stored.approval_evidence["market_evidence"]["count"] == 0
    assert stored.approval_evidence["market_evidence"]["status"] == "INSUFFICIENT_MARKET_DATA"


def test_pass_validation_can_be_approved(approval_context):
    _, service, _, admin, product, _ = approval_context
    product.supplier_validation_status = "PASS"
    service.db.commit()
    assert service.approve(product.id, admin).commercial_status == "APPROVED"


def test_variant_priced_product_does_not_require_product_level_supplier_cost(approval_context):
    _, service, _, admin, product, _ = approval_context
    product.supplier_cost = None
    service.db.commit()

    result = service.approve(product.id, admin)

    assert result.commercial_status == "APPROVED"
    assert result.supplier_cost is None


def test_cac_unsupported_is_informational(approval_context):
    db, service, _, admin, product, _ = approval_context
    current = service.launch_pricing_policy
    policy = LaunchPricingPolicy(
        pricing_fx_rate=current.pricing_fx_rate,
        payment_gateway_pct=current.payment_gateway_pct,
        rto_reserve_pct=current.rto_reserve_pct,
        target_contribution_margin_pct=current.target_contribution_margin_pct,
        target_cac_inr=Decimal("100000"),
    )
    result = AdminProductService(db, launch_pricing_policy=policy).approve(product.id, admin)
    assert result.commercial_status == "APPROVED"
    assert "CAC_TARGET_NOT_SUPPORTED" in result.commercial_reasons


@pytest.mark.parametrize(("mutation", "expected"), [
    ("validation_missing", "VALIDATION_NOT_AVAILABLE"),
    ("validation_reject", "SUPPLIER_VALIDATION_REJECTED"),
    ("shipping_missing", "SHIPPING_COST_MISSING"),
    ("shipping_invalid", "SHIPPING_COST_INVALID"),
    ("variant_cost_missing", "SUPPLIER_COST_MISSING"),
    ("variant_price_missing", "VARIANT_PRICE_MISSING"),
    ("variant_price_mismatch", "VARIANT_PRICE_DISCREPANCY"),
    ("target_margin_not_met", "TARGET_MARGIN_NOT_MET"),
    ("no_cj_inventory", "NO_SELLABLE_INVENTORY"),
    ("incomplete_product", "INCOMPLETE_PRODUCT_DATA"),
])
def test_critical_blocker_prevents_approval_without_persistence(approval_context, mutation, expected):
    db, service, _, admin, product, variant = approval_context
    if mutation == "validation_missing": product.supplier_validation_status = None
    elif mutation == "validation_reject": product.supplier_validation_status = "REJECT"
    elif mutation == "shipping_missing": product.shipping_cost = None
    elif mutation == "shipping_invalid": product.shipping_cost = Decimal("-1")
    elif mutation == "variant_cost_missing": variant.supplier_cost_usd = None
    elif mutation == "variant_price_missing": variant.selling_price = None
    elif mutation == "variant_price_mismatch": variant.selling_price += Decimal("1")
    elif mutation == "target_margin_not_met": variant.selling_price = Decimal("250")
    elif mutation == "no_cj_inventory": product.cj_inventory = 0
    else: product.name = " "
    db.commit()
    with pytest.raises(BadRequestError) as exc:
        service.approve(product.id, admin)
    db.refresh(product)
    assert expected in exc.value.detail
    assert product.commercial_status == "REVIEW"
    assert product.approval_decided_at is None
    assert product.approval_decided_by_user_id is None
    assert product.approval_evidence is None


def test_rejection_trims_reason_and_records_admin(approval_context):
    db, service, _, admin, product, _ = approval_context
    result = service.reject(product.id, ProductRejectionRequest(reason="  weak demand  "), admin)
    stored = db.get(Product, product.id)
    assert result.commercial_status == "REJECTED" and result.status == "DRAFT"
    assert stored.approval_rejection_reason == "weak demand"
    assert stored.approval_decided_by_user_id == admin.id
    assert stored.approval_evidence["decision"] == "REJECTED"


def test_rejection_reason_is_optional(approval_context):
    _, service, _, admin, product, _ = approval_context
    assert service.reject(product.id, ProductRejectionRequest(), admin).approval_rejection_reason is None


def test_rejection_reason_max_length_is_validated(approval_context):
    _, _, client, _, product, _ = approval_context
    response = client.post(f"/api/v1/admin/products/{product.id}/reject", json={"reason": "x" * 501})
    assert response.status_code == 422


def test_reject_without_body_is_supported(approval_context):
    _, _, client, _, product, _ = approval_context
    response = client.post(f"/api/v1/admin/products/{product.id}/reject")
    assert response.status_code == 200
    assert response.json()["commercial_status"] == "REJECTED"


def test_active_product_must_be_paused_before_rejection(approval_context):
    _, service, _, admin, product, _ = approval_context
    product.status = "ACTIVE"
    service.db.commit()
    with pytest.raises(BadRequestError, match="Pause active product"):
        service.reject(product.id, ProductRejectionRequest(), admin)


def test_rejected_product_cannot_activate(approval_context):
    _, service, _, admin, product, _ = approval_context
    service.reject(product.id, ProductRejectionRequest(), admin)
    with pytest.raises(BadRequestError, match="APPROVED"):
        service.activate(product.id)


def test_approved_draft_activates(approval_context):
    db, service, _, admin, product, _ = approval_context
    service.approve(product.id, admin)
    make_activation_ready(db, product)
    result = service.activate(product.id)
    assert result.status == "ACTIVE" and result.commercial_status == "APPROVED"


def test_unapproved_draft_cannot_activate(approval_context):
    _, service, _, _, product, _ = approval_context
    with pytest.raises(BadRequestError, match="APPROVED"):
        service.activate(product.id)


def test_active_product_pauses(approval_context):
    _, service, _, _, product, _ = approval_context
    product.status, product.commercial_status = "ACTIVE", "APPROVED"
    service.db.commit()
    assert service.pause(product.id).status == "PAUSED"


def test_draft_product_cannot_pause(approval_context):
    _, service, _, _, product, _ = approval_context
    with pytest.raises(BadRequestError, match="ACTIVE"):
        service.pause(product.id)


def test_paused_approved_product_reactivates(approval_context):
    db, service, _, _, product, _ = approval_context
    product.status, product.commercial_status = "PAUSED", "APPROVED"
    service.db.commit()
    make_activation_ready(db, product)
    assert service.activate(product.id).status == "ACTIVE"


def test_paused_rejected_product_cannot_reactivate(approval_context):
    _, service, _, _, product, _ = approval_context
    product.status, product.commercial_status = "PAUSED", "REJECTED"
    service.db.commit()
    with pytest.raises(BadRequestError, match="APPROVED"):
        service.activate(product.id)


@pytest.mark.parametrize("status", ["ACTIVE", "PAUSED"])
def test_supplier_patch_cannot_bypass_lifecycle(approval_context, status):
    _, service, _, _, product, _ = approval_context
    with pytest.raises(BadRequestError, match="activate or pause"):
        service.update_status(product.id, ProductStatusUpdate(status=status))


def test_supplier_draft_patch_is_idempotent(approval_context):
    _, service, _, _, product, _ = approval_context
    assert service.update_status(product.id, ProductStatusUpdate(status="DRAFT")).status == "DRAFT"


def test_legacy_product_patch_behavior_is_preserved(approval_context):
    db, service, _, _, _, _ = approval_context
    legacy = Product(id=uuid4(), slug=f"phase36-legacy-{uuid4()}", name="Legacy", description="Legacy", status="DRAFT")
    db.add(legacy)
    db.commit()
    try:
        assert service.update_status(legacy.id, ProductStatusUpdate(status="ACTIVE")).status == "ACTIVE"
    finally:
        db.delete(legacy)
        db.commit()


@pytest.mark.parametrize("action", ["approve", "reject", "activate", "pause"])
def test_final_gate_routes_require_authentication(approval_context, action):
    _, _, _, _, product, _ = approval_context
    app.dependency_overrides.clear()
    assert TestClient(app).post(f"/api/v1/admin/products/{product.id}/{action}").status_code == 401


def test_route_uses_dependency_admin_identity(approval_context):
    _, _, client, admin, product, _ = approval_context
    response = client.post(
        f"/api/v1/admin/products/{product.id}/approve",
        json={"approval_decided_by_user_id": str(uuid4())},
    )
    assert response.status_code == 200
    assert response.json()["approval_decided_by_user_id"] == str(admin.id)


def test_approval_preserves_commercial_inputs(approval_context):
    db, service, _, admin, product, variant = approval_context
    before = immutable_state(product, variant)
    evidence = ProductMarketEvidence(
        product_id=product.id, competitor_name="Fixture", product_name="Comparable",
        source_url="https://example.com/comparable", observed_price_inr=Decimal("499"),
    )
    db.add(evidence)
    db.commit()
    service.approve(product.id, admin)
    db.refresh(product)
    db.refresh(variant)
    assert immutable_state(product, variant) == before
    assert db.get(ProductMarketEvidence, evidence.id) is not None


def test_rejection_preserves_commercial_inputs(approval_context):
    db, service, _, admin, product, variant = approval_context
    before = immutable_state(product, variant)
    service.reject(product.id, ProductRejectionRequest(reason="No fit"), admin)
    db.refresh(product)
    db.refresh(variant)
    assert immutable_state(product, variant) == before


def test_repeated_approval_is_idempotent_but_rechecks_blockers(approval_context):
    db, service, _, admin, product, _ = approval_context
    decided_at = service.approve(product.id, admin).approval_decided_at
    assert service.approve(product.id, admin).approval_decided_at == decided_at
    product.cj_inventory = 0
    db.commit()
    with pytest.raises(BadRequestError, match="NO_SELLABLE_INVENTORY"):
        service.approve(product.id, admin)


def test_activate_and_pause_are_idempotent(approval_context):
    db, service, _, admin, product, _ = approval_context
    service.approve(product.id, admin)
    make_activation_ready(db, product)
    assert service.activate(product.id).status == "ACTIVE"
    assert service.activate(product.id).status == "ACTIVE"
    assert service.pause(product.id).status == "PAUSED"
    assert service.pause(product.id).status == "PAUSED"


def test_final_decision_blocks_automatic_commercial_review(approval_context):
    _, service, _, admin, product, _ = approval_context
    service.approve(product.id, admin)
    with pytest.raises(BadRequestError, match="Final commercial decision"):
        service.commercial_review(product.id)