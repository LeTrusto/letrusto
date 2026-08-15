import asyncio
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_admin_product_service, get_current_admin
from app.core.exceptions import BadRequestError
from app.main import app
from app.db.session import SessionLocal
from app.models.entities import Brand, Category, Product
from app.services.admin_product_service import AdminProductService
from app.suppliers.base import RawSupplierProduct, RawVariant, ShippingOption, ShippingResult, ShippingValidation


class FakeAdapter:
    supplier_name = "cj"

    async def authenticate(self) -> bool:
        return True

    async def get_product(self, product_id: str) -> RawSupplierProduct:
        variant = RawVariant(
            supplier_variant_id="VID-TEST-001",
            supplier_variant_sku="CJ-TEST-001-RED",
            name="Red",
            option_key="Red",
            price_usd=2.0,
            weight_grams=20.0,
            inventory=50,
            total_inventory=1050,
            cj_inventory=50,
            factory_inventory=1000,
            inventory_verification="unverified",
        )
        return RawSupplierProduct(
            supplier_id="cj",
            supplier_product_id=product_id,
            supplier_sku="CJ-TEST-001",
            title="Test Hair Clip",
            description="Validated test product",
            images=["https://example.com/test-image.jpg", "https://example.com/test-image-2.jpg"],
            price_usd=2.0,
            weight_grams=20.0,
            variants=[variant],
            inventory_total=50,
            total_inventory=1050,
            cj_inventory=50,
            factory_inventory=1000,
            inventory_verification="unverified",
            warehouse_country="CN",
        )

    async def calculate_shipping(self, *args, **kwargs) -> ShippingResult:
        return ShippingResult(
            can_ship=True,
            validation=ShippingValidation.VERIFIED,
            options=[ShippingOption(carrier="Test", method="Test", cost_usd=2.0, estimated_days="10-15")],
            origin_country="CN",
            destination_country="IN",
        )


def test_import_is_draft_and_preserves_supplier_data(monkeypatch):
    import app.services.admin_product_service as module
    from app.schemas.admin_products import ProductImportRequest

    monkeypatch.setattr(module, "build_supplier_adapter", lambda _: FakeAdapter())
    db = SessionLocal()
    service = AdminProductService(db)
    product_id = "phase31-test-product"
    try:
        result = asyncio.run(service.import_product(ProductImportRequest(supplier="cj", supplier_product_id=product_id)))
        assert result.status == "DRAFT"
        assert result.supplier_product_id == product_id
        assert result.cj_inventory == 50
        assert result.factory_inventory == 1000
        assert result.total_inventory == 1050
        assert result.supplier_cost == Decimal("167.00")
        assert result.shipping_cost == Decimal("167.00")
        assert len(result.images) == 2
        assert result.variants[0].supplier_variant_id == "VID-TEST-001"
        assert result.variants[0].supplier_cost == Decimal("167.00")
        assert result.variants[0].supplier_cost_usd == Decimal("2.0000")
        assert result.variants[0].cj_inventory == 50
        assert result.variants[0].factory_inventory == 1000
    finally:
        db.query(Product).filter(Product.supplier_product_id == product_id).delete(synchronize_session=False)
        db.commit()
        db.close()


class VariantOnlyCostAdapter(FakeAdapter):
    async def get_product(self, product_id: str) -> RawSupplierProduct:
        product = await super().get_product(product_id)
        product.price_usd = None
        product.variants[0].price_usd = 1.09
        product.weight_grams = None
        return product


def test_import_preserves_variant_cost_without_inventing_product_cost(monkeypatch):
    import app.services.admin_product_service as module
    from app.schemas.admin_products import ProductImportRequest

    monkeypatch.setattr(module, "build_supplier_adapter", lambda _: VariantOnlyCostAdapter())
    db = SessionLocal()
    service = AdminProductService(db)
    product_id = "phase31-variant-only-cost"
    try:
        result = asyncio.run(
            service.import_product(
                ProductImportRequest(supplier="cj", supplier_product_id=product_id)
            )
        )

        assert result.supplier_cost is None
        assert result.variants[0].supplier_cost == Decimal("91.02")
        assert result.variants[0].supplier_cost_usd == Decimal("1.0900")
        assert result.shipping_cost == Decimal("167.00")
        assert result.cj_inventory == 50
        assert result.factory_inventory == 1000
        assert result.supplier_validation_details["missing_fields"] == ["price", "weight", "category"]
        assert result.supplier_validation_details["variants"][0]["cost_usd"] == 1.09
        assert result.supplier_validation_details["variants"][0]["weight_grams"] == 20.0
    finally:
        db.query(Product).filter(Product.supplier_product_id == product_id).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


class HairClipEvidenceAdapter(FakeAdapter):
    async def get_product(self, product_id: str) -> RawSupplierProduct:
        product = await super().get_product(product_id)
        product.weight_grams = None
        return product


def test_import_reuses_phase2_scoring_once_and_persists_exact_hair_clip_evidence(monkeypatch):
    import app.services.admin_product_service as module
    from app.schemas.admin_products import ProductImportRequest

    calls = []
    existing_score_product = module.score_product

    def scoring_spy(normalized, economics=None, shipping=None):
        calls.append((normalized, economics, shipping))
        return existing_score_product(normalized, economics=economics, shipping=shipping)

    monkeypatch.setattr(module, "build_supplier_adapter", lambda _: HairClipEvidenceAdapter())
    monkeypatch.setattr(module, "score_product", scoring_spy)
    db = SessionLocal()
    service = AdminProductService(db)
    product_id = "phase342-hair-clip-evidence"
    try:
        result = asyncio.run(
            service.import_product(
                ProductImportRequest(supplier="cj", supplier_product_id=product_id)
            )
        )

        assert len(calls) == 1
        assert result.status == "DRAFT"
        assert result.supplier_validation_status == "REVIEW"
        assert result.supplier_validation_score == 61
        assert result.supplier_validation_notes == [
            "Margin unknown — missing cost inputs",
            "Missing: weight, category",
        ]
        assert result.supplier_validated_at is not None
        assert result.supplier_validation_details["breakdown"] == {
            "supplier_reliability": 12,
            "shipping_feasibility": 25,
            "margin_score": 5,
            "inventory_score": 5,
            "data_completeness": 6,
            "return_risk": 8,
        }
        assert result.supplier_validation_details["calculation_origin"] == "IMPORT"
        assert result.supplier_validation_details["historical_evidence_available"] is True
        assert result.supplier_validation_details["unknown_costs"] == ["rto_reserve"]
        stored = db.query(Product).filter(Product.supplier_product_id == product_id).one()
        assert stored.supplier_validation_status == "REVIEW"
        assert stored.supplier_validation_score == 61
        assert stored.supplier_validation_notes == result.supplier_validation_notes
        assert stored.supplier_validated_at is not None
    finally:
        db.query(Product).filter(Product.supplier_product_id == product_id).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_import_route_reaches_service_and_persists_supplier_product(monkeypatch):
    import app.services.admin_product_service as module

    monkeypatch.setattr(module, "build_supplier_adapter", lambda _: FakeAdapter())
    db = SessionLocal()
    service = AdminProductService(db)
    product_id = "phase31-route-product"
    app.dependency_overrides[get_current_admin] = lambda: object()
    app.dependency_overrides[get_admin_product_service] = lambda: service
    try:
        response = TestClient(app).post(
            "/api/v1/admin/products/import",
            json={"supplier": "cj", "supplier_product_id": product_id, "destination": "IN"},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "DRAFT"
        assert db.query(Product).filter(Product.supplier_product_id == product_id).count() == 1
    finally:
        app.dependency_overrides.clear()
        db.query(Product).filter(Product.supplier_product_id == product_id).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_import_is_idempotent_and_supplier_status_patch_is_gated(monkeypatch):
    import app.services.admin_product_service as module
    from app.schemas.admin_products import ProductImportRequest, ProductStatusUpdate

    monkeypatch.setattr(module, "build_supplier_adapter", lambda _: FakeAdapter())
    db = SessionLocal()
    service = AdminProductService(db)
    product_id = "phase31-idempotent-product"
    try:
        payload = ProductImportRequest(supplier="cj", supplier_product_id=product_id)
        first = asyncio.run(service.import_product(payload))
        second = asyncio.run(service.import_product(payload))
        assert first.id == second.id
        assert db.query(Product).filter(Product.supplier == "cj", Product.supplier_product_id == product_id).count() == 1

        assert service.update_status(first.id, ProductStatusUpdate(status="DRAFT")).status == "DRAFT"
        with pytest.raises(BadRequestError, match="activate or pause"):
            service.update_status(first.id, ProductStatusUpdate(status="ACTIVE"))
        with pytest.raises(BadRequestError, match="activate or pause"):
            service.update_status(first.id, ProductStatusUpdate(status="PAUSED"))
    finally:
        db.query(Product).filter(Product.supplier_product_id == product_id).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_admin_catalog_separates_legacy_and_supplier_products():
    db = SessionLocal()
    service = AdminProductService(db)
    suffix = str(uuid4())[:8]
    category = Category(name=f"Phase31 Category {suffix}", slug=f"phase31-category-{suffix}")
    brand = Brand(name=f"Phase31 Brand {suffix}", slug=f"phase31-brand-{suffix}")
    db.add_all([category, brand])
    db.flush()
    legacy = Product(id=uuid4(), slug=f"phase31-legacy-{suffix}", name="Legacy product", description="Legacy", status="ACTIVE", category_id=category.id, brand_id=brand.id)
    supplier = Product(id=uuid4(), slug=f"phase31-cj-{suffix}", name="CJ product", description="CJ", status="DRAFT", supplier="cj", supplier_product_id=f"phase31-cj-{suffix}")
    db.add_all([legacy, supplier])
    db.commit()
    try:
        default = service.list_products(None, None, 0, 100)
        assert all(product.supplier is not None for product in default.products)
        assert supplier.id in {product.id for product in default.products}
        assert legacy.id not in {product.id for product in default.products}

        filtered = service.list_products(None, "cj", 0, 100)
        filtered_ids = {product.id for product in filtered.products}
        assert supplier.id in filtered_ids
        assert legacy.id not in filtered_ids
        assert all(product.supplier == "cj" for product in filtered.products)
        assert db.get(Product, legacy.id).status == "ACTIVE"
    finally:
        db.delete(supplier)
        db.delete(legacy)
        db.delete(brand)
        db.delete(category)
        db.commit()
        db.close()
