from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api.deps import get_admin_product_service, get_current_admin
from app.db.session import SessionLocal
from app.main import app
from app.models.entities import Product, ProductImage, ProductMarketEvidence, ProductVariant
from app.services.admin_product_service import AdminProductService


def _product(suffix: str, commercial_status: str, status: str = "DRAFT") -> Product:
    product = Product(
        id=uuid4(),
        slug=f"phase37a-{suffix}",
        name=f"Phase 3.7A {suffix}",
        description="Bulk approved import preservation fixture",
        status=status,
        supplier="cj",
        supplier_product_id=f"CJ-PID-{suffix}",
        supplier_source_url=f"https://cjdropshipping.com/product/{suffix}",
        supplier_cost=Decimal("123.45"),
        shipping_cost=Decimal("67.89"),
        selling_price=Decimal("499.00"),
        currency="INR",
        total_inventory=1099,
        cj_inventory=99,
        factory_inventory=1000,
        verified_warehouse="verified",
        commercial_status=commercial_status,
        commercial_reasons=["fixture evidence"],
        supplier_validation_status="PASS",
        supplier_validation_score=91,
        supplier_validation_notes=["preserve me"],
        supplier_validation_details={"calculation_origin": "IMPORT", "score": 91},
        approval_evidence={"decision": commercial_status, "market_price_status": "MARKET_COMPETITIVE"},
    )
    product.images.append(
        ProductImage(url=f"https://example.com/{suffix}.jpg", position=1)
    )
    product.variants.append(
        ProductVariant(
            supplier_variant_id=f"CJ-VID-{suffix}",
            supplier_variant_sku=f"CJ-SKU-{suffix}",
            name="Default",
            attributes="Default",
            supplier_cost=Decimal("123.45"),
            supplier_cost_usd=Decimal("1.4784"),
            selling_price=Decimal("499.00"),
            total_inventory=1099,
            cj_inventory=99,
            factory_inventory=1000,
            verified_warehouse="verified",
            weight_grams=Decimal("125.00"),
            active=True,
            position=1,
        )
    )
    product.market_evidence.append(
        ProductMarketEvidence(
            competitor_name="Fixture Market",
            product_name=f"Comparable {suffix}",
            source_url=f"https://example.com/market/{suffix}",
            observed_price_inr=Decimal("549.00"),
            currency="INR",
            variant_description="Default",
            notes="Preserve market evidence",
        )
    )
    return product


def _snapshot(product: Product) -> dict:
    def columns(instance) -> dict:
        return {
            column.name: getattr(instance, column.name)
            for column in instance.__table__.columns
        }

    return {
        "product": columns(product),
        "images": [columns(image) for image in product.images],
        "variants": [columns(variant) for variant in product.variants],
        "market_evidence": [columns(evidence) for evidence in product.market_evidence],
    }


def test_bulk_import_requires_admin_authentication():
    response = TestClient(app).post(
        "/api/v1/admin/products/bulk-import",
        json={"supplier": "cj", "product_ids": ["CJ-PID-UNAUTHORIZED"]},
    )

    assert response.status_code == 401


def test_bulk_import_requires_candidates_without_mutating_existing_products(monkeypatch):
    import app.services.admin_product_service as service_module

    monkeypatch.setattr(
        service_module,
        "build_supplier_adapter",
        lambda *_: (_ for _ in ()).throw(AssertionError("bulk import must not call CJ")),
    )
    db = SessionLocal()
    service = AdminProductService(db)
    suffix = str(uuid4())[:8]
    approved_draft = _product(f"approved-draft-{suffix}", "APPROVED")
    approved_paused = _product(f"approved-paused-{suffix}", "APPROVED", "PAUSED")
    commercial_draft = _product(f"commercial-draft-{suffix}", "DRAFT")
    review = _product(f"review-{suffix}", "REVIEW")
    rejected = _product(f"rejected-{suffix}", "REJECTED")
    products = [approved_draft, approved_paused, commercial_draft, review, rejected]
    db.add_all(products)
    db.commit()
    snapshots = {product.id: _snapshot(product) for product in products}
    initial_product_count = db.scalar(select(func.count(Product.id)))
    app.dependency_overrides[get_current_admin] = lambda: object()
    app.dependency_overrides[get_admin_product_service] = lambda: service
    requested_ids = [
        approved_draft.supplier_product_id,
        approved_paused.supplier_product_id,
        approved_draft.supplier_product_id,
        approved_paused.variants[0].supplier_variant_sku,
        commercial_draft.supplier_product_id,
        review.supplier_product_id,
        rejected.supplier_product_id,
        f"CJ-PID-MISSING-{suffix}",
    ]
    try:
        response = TestClient(app).post(
            "/api/v1/admin/products/bulk-import",
            json={"supplier": "cj", "product_ids": requested_ids},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["requested_count"] == 8
        assert body["imported_count"] == 0
        assert body["already_exists_count"] == 0
        assert body["already_imported_count"] == 0
        assert body["rejected_not_approved_count"] == 8
        assert body["failed_count"] == 0
        assert [result["requested_id"] for result in body["results"]] == requested_ids
        assert [result["status"] for result in body["results"]] == [
            "REJECTED_NOT_APPROVED",
            "REJECTED_NOT_APPROVED",
            "REJECTED_NOT_APPROVED",
            "REJECTED_NOT_APPROVED",
            "REJECTED_NOT_APPROVED",
            "REJECTED_NOT_APPROVED",
            "REJECTED_NOT_APPROVED",
            "REJECTED_NOT_APPROVED",
        ]
        assert all(result["canonical_supplier_product_id"] is None for result in body["results"])
        assert all(result["product_id"] is None for result in body["results"])
        assert db.scalar(select(func.count(Product.id))) == initial_product_count

        db.expire_all()
        for product in products:
            stored = db.get(Product, product.id)
            assert stored is not None
            assert _snapshot(stored) == snapshots[product.id]
        assert db.get(Product, approved_draft.id).status == "DRAFT"
        assert db.get(Product, approved_paused.id).status == "PAUSED"
        assert db.get(Product, commercial_draft.id).commercial_status == "DRAFT"
        assert db.get(Product, review.id).commercial_status == "REVIEW"
        assert db.get(Product, rejected.id).commercial_status == "REJECTED"
    finally:
        app.dependency_overrides.clear()
        for product in products:
            stored = db.get(Product, product.id)
            if stored is not None:
                db.delete(stored)
        db.commit()
        db.close()


def test_bulk_import_request_validation():
    app.dependency_overrides[get_current_admin] = lambda: object()
    try:
        client = TestClient(app)
        empty = client.post(
            "/api/v1/admin/products/bulk-import",
            json={"supplier": "cj", "product_ids": []},
        )
        blank = client.post(
            "/api/v1/admin/products/bulk-import",
            json={"supplier": "cj", "product_ids": ["   "]},
        )
        too_many = client.post(
            "/api/v1/admin/products/bulk-import",
            json={"supplier": "cj", "product_ids": [str(index) for index in range(101)]},
        )
        unsupported_supplier = client.post(
            "/api/v1/admin/products/bulk-import",
            json={"supplier": "other", "product_ids": ["product"]},
        )

        assert empty.status_code == 422
        assert blank.status_code == 422
        assert too_many.status_code == 422
        assert unsupported_supplier.status_code == 422
    finally:
        app.dependency_overrides.clear()