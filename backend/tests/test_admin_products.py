import asyncio
from copy import deepcopy
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_admin_product_service, get_current_admin
from app.core.exceptions import BadRequestError
from app.main import app
from app.db.session import SessionLocal
from app.models.entities import Brand, Category, Product, ProductVariant, SupplierCandidate, SupplierVariantInventory
from app.services.admin_product_service import AdminProductService
from app.suppliers.base import (
    RawSupplierProduct,
    RawVariant,
    ShippingOption,
    ShippingResult,
    ShippingValidation,
    WarehouseInventorySnapshot,
)


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
            warehouses=[WarehouseInventorySnapshot("CN", "1", "China Warehouse", 1050, 50, 1000, "unverified")],
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


class BatchFakeAdapter(FakeAdapter):
    async def search_products(self, keyword: str, *, page_size: int = 20, **kwargs):
        results = []
        for index in range(min(page_size, 2)):
            product = await self.get_product(f"phase31-discovered-{index}")
            results.append(product)
        return results


class ConfigurableDiscoveryAdapter(BatchFakeAdapter):
    def __init__(self, count: int = 1, *, failure_id: str | None = None, no_inventory: bool = False, no_freight: bool = False, invalid_vid: bool = False, multiple_warehouses: bool = False, multiple_variants: bool = False) -> None:
        self.count = count
        self.failure_id = failure_id
        self.no_inventory = no_inventory
        self.no_freight = no_freight
        self.invalid_vid = invalid_vid
        self.multiple_warehouses = multiple_warehouses
        self.multiple_variants = multiple_variants

    async def search_products(self, keyword: str, *, page_size: int = 20, **kwargs):
        results = []
        for index in range(min(page_size, self.count)):
            product = await FakeAdapter.get_product(self, f"phase1-{index:02d}")
            product.supplier_product_id = f"phase1-{index:02d}"
            results.append(product)
        return results

    async def get_product(self, product_id: str, *, strict: bool = False):
        if product_id == self.failure_id:
            raise RuntimeError("detail unavailable")
        product = await FakeAdapter.get_product(self, product_id)
        product.supplier_product_id = product_id
        if self.no_inventory:
            product.cj_inventory = 0
            product.inventory_total = 0
            for variant in product.variants:
                variant.cj_inventory = 0
        if self.invalid_vid:
            product.variants[0].supplier_variant_id = ""
        if self.multiple_warehouses:
            product.variants[0].warehouses.append(
                WarehouseInventorySnapshot("IN", "in-1", "India Warehouse", 40, 40, 0, "verified")
            )
        if self.multiple_variants:
            product.variants.append(deepcopy(product.variants[0]))
            product.variants[1].supplier_variant_id = "VID-SECONDARY"
            product.variants[1].supplier_variant_sku = "SKU-SECONDARY"
        return product

    async def calculate_shipping(self, *args, **kwargs) -> ShippingResult:
        if self.no_freight:
            return ShippingResult(
                can_ship=False,
                validation=ShippingValidation.NOT_AVAILABLE,
                options=[],
                origin_country="CN",
                destination_country="IN",
                error="No route",
            )
        return await FakeAdapter.calculate_shipping(self, *args, **kwargs)


def run_candidate_discovery(monkeypatch, adapter, *, page_size=1, keyword="phase 1"):
    import app.services.admin_product_service as module
    from app.schemas.admin_products import SupplierCandidateDiscoveryRequest

    monkeypatch.setattr(module, "build_supplier_adapter", lambda _: adapter)
    db = SessionLocal()
    service = AdminProductService(db)
    result = asyncio.run(service.discover_supplier_candidates(SupplierCandidateDiscoveryRequest(
        supplier="cj", keyword=keyword, page_size=page_size,
    )))
    return db, result


def cleanup_discovery_rows(db, product_ids):
    db.query(SupplierCandidate).filter(SupplierCandidate.supplier_product_id.in_(product_ids)).delete(synchronize_session=False)
    db.query(Product).filter(Product.supplier_product_id.in_(product_ids)).delete(synchronize_session=False)
    db.commit()
    db.close()


def test_phase1_one_product_duplicate_discovery_and_no_import_or_activation(monkeypatch):
    adapter = ConfigurableDiscoveryAdapter()
    db, first = run_candidate_discovery(monkeypatch, adapter)
    try:
        assert (first.staged_count, first.failed_count) == (1, 0)
        assert first.results[0].candidate.readiness_status in {"VALIDATED", "REVIEW"}
        assert first.results[0].candidate.approval_status == "REVIEW"
        assert db.query(Product).filter(Product.supplier_product_id == "phase1-00").count() == 0
        _, second = run_candidate_discovery(monkeypatch, adapter)
        assert second.already_staged_count == 1
    finally:
        cleanup_discovery_rows(db, {"phase1-00"})


def test_phase1_fifty_product_batch_is_bounded_and_deduplicated(monkeypatch):
    db, result = run_candidate_discovery(monkeypatch, ConfigurableDiscoveryAdapter(count=50), page_size=50)
    try:
        assert result.requested_count == result.staged_count == 50
        assert db.query(SupplierCandidate).filter(SupplierCandidate.supplier_product_id.like("phase1-%")).count() == 50
    finally:
        cleanup_discovery_rows(db, {f"phase1-{index:02d}" for index in range(50)})


def test_phase1_partial_failure_is_reported_without_aborting_batch(monkeypatch):
    db, result = run_candidate_discovery(monkeypatch, ConfigurableDiscoveryAdapter(count=3, failure_id="phase1-01"), page_size=3)
    try:
        assert result.staged_count == 2
        assert result.failed_count == 1
        assert next(item for item in result.results if item.supplier_product_id == "phase1-01").status == "FAILED"
    finally:
        cleanup_discovery_rows(db, {"phase1-00", "phase1-01", "phase1-02"})


@pytest.mark.parametrize("option", ["no_inventory", "no_freight", "invalid_vid"])
def test_phase1_deterministic_fulfillment_gates_reject_candidates(monkeypatch, option):
    db, result = run_candidate_discovery(monkeypatch, ConfigurableDiscoveryAdapter(**{option: True}))
    try:
        candidate = result.results[0].candidate
        assert candidate is not None
        assert candidate.readiness_status == "REJECTED"
        assert candidate.approval_status == "REVIEW"
        assert candidate.commercial_result["failure_reasons"]
    finally:
        cleanup_discovery_rows(db, {"phase1-00"})


def test_phase1_snapshot_preserves_multiple_warehouses_and_variants(monkeypatch):
    db, result = run_candidate_discovery(monkeypatch, ConfigurableDiscoveryAdapter(multiple_warehouses=True, multiple_variants=True))
    try:
        candidate = result.results[0].candidate
        assert candidate is not None
        assert len(candidate.variants) == 2
        assert len(candidate.warehouses) == 4
        assert candidate.freight["available"] is True
        assert candidate.logistics["selected"]["method"] == "Test"
    finally:
        cleanup_discovery_rows(db, {"phase1-00"})


def test_phase1_pricing_failure_is_rejected_and_recorded(monkeypatch):
    import app.services.admin_product_service as module

    def fail_pricing(*args, **kwargs):
        raise ValueError("pricing policy failure")

    monkeypatch.setattr(module, "calculate_launch_variant_price", fail_pricing)
    db, result = run_candidate_discovery(monkeypatch, ConfigurableDiscoveryAdapter())
    try:
        candidate = result.results[0].candidate
        assert candidate is not None
        assert candidate.readiness_status == "REJECTED"
        assert "pricing policy failure" in candidate.commercial_result["failure_reasons"]
    finally:
        cleanup_discovery_rows(db, {"phase1-00"})


def test_discovery_stages_bounded_candidates_without_importing(monkeypatch):
    import app.services.admin_product_service as module
    from app.schemas.admin_products import SupplierCandidateDiscoveryRequest

    monkeypatch.setattr(module, "build_supplier_adapter", lambda _: BatchFakeAdapter())
    db = SessionLocal()
    service = AdminProductService(db)
    product_ids = {"phase31-discovered-0", "phase31-discovered-1"}
    try:
        result = asyncio.run(service.discover_supplier_candidates(SupplierCandidateDiscoveryRequest(
            supplier="cj", keyword="hair clip", page_size=2,
        )))
        assert result.requested_count == 2
        assert result.staged_count == 2
        assert result.failed_count == 0
        assert all(item.status == "STAGED" for item in result.results)
        candidates = db.query(SupplierCandidate).filter(
            SupplierCandidate.supplier_product_id.in_(product_ids)
        ).all()
        assert len(candidates) == 2
        assert all(candidate.approval_status == "REVIEW" for candidate in candidates)
        assert db.query(Product).filter(Product.supplier_product_id.in_(product_ids)).count() == 0
    finally:
        db.query(SupplierCandidate).filter(
            SupplierCandidate.supplier_product_id.in_(product_ids)
        ).delete(synchronize_session=False)
        db.commit()
        db.close()


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
        warehouse_rows = db.query(SupplierVariantInventory).filter(
            SupplierVariantInventory.product_id == result.id,
        ).all()
        assert len(warehouse_rows) == 1
        assert warehouse_rows[0].supplier_variant_id == "VID-TEST-001"
        assert warehouse_rows[0].storage_id == "1"
        assert warehouse_rows[0].warehouse_name == "China Warehouse"
        assert warehouse_rows[0].warehouse_country == "CN"
        assert warehouse_rows[0].cj_sellable_inventory == 50
        assert warehouse_rows[0].factory_inventory == 1000
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


def test_public_catalog_exposes_only_safe_active_variant_data():
    from app.api.deps import get_product_service

    db = SessionLocal()
    suffix = str(uuid4())[:8]
    category = Category(name=f"Public Category {suffix}", slug=f"public-category-{suffix}")
    brand = Brand(name=f"Public Brand {suffix}", slug=f"public-brand-{suffix}")
    db.add_all([category, brand])
    db.flush()
    product = Product(
        id=uuid4(), slug=f"public-product-{suffix}", name="Public product", description="Public",
        status="ACTIVE", supplier="cj", supplier_product_id=f"cj-{suffix}", category_id=category.id,
        brand_id=brand.id, price_value=Decimal("299.00"), selling_price=Decimal("299.00"),
        ai_score=80, rating=Decimal("4.0"), availability="In Stock", ai_summary="Public summary",
        review_summary="Public reviews",
    )
    product.variants = [
        ProductVariant(
            supplier_variant_id=f"VID-{suffix}", supplier_variant_sku=f"SKU-{suffix}", name="Red",
            selling_price=Decimal("299.00"), cj_inventory=4, factory_inventory=999, active=True, position=1,
        ),
        ProductVariant(
            supplier_variant_id=f"VID-OUT-{suffix}", supplier_variant_sku=f"SKU-OUT-{suffix}", name="Blue",
            selling_price=Decimal("399.00"), cj_inventory=0, factory_inventory=999, active=True, position=2,
        ),
    ]
    db.add(product)
    db.commit()
    service = get_product_service(db)
    try:
        response = service.get_product(product.slug)
        assert [variant.label for variant in response.variants] == ["Red", "Blue"]
        assert response.variants[0].priceValue == Decimal("299.00")
        assert response.variants[0].available is True
        assert response.variants[0].inventory == 4
        assert response.variants[1].available is False
        serialized = response.model_dump_json()
        assert f"VID-{suffix}" not in serialized
        assert f"SKU-{suffix}" not in serialized
        assert "factory_inventory" not in serialized
        assert "supplier_cost" not in serialized
    finally:
        db.delete(product)
        db.delete(brand)
        db.delete(category)
        db.commit()
        db.close()


def test_public_catalog_hides_active_product_without_stored_customer_price():
    from app.services.product_service import ProductService
    from app.repositories.product_repository import ProductRepository

    db = SessionLocal()
    suffix = str(uuid4())[:8]
    category = Category(name=f"Unpriced Category {suffix}", slug=f"unpriced-category-{suffix}")
    brand = Brand(name=f"Unpriced Brand {suffix}", slug=f"unpriced-brand-{suffix}")
    db.add_all([category, brand])
    db.flush()
    product = Product(
        id=uuid4(), slug=f"unpriced-product-{suffix}", name="Unpriced product", description="Unpriced",
        status="ACTIVE", category_id=category.id, brand_id=brand.id, ai_score=1, rating=Decimal("1.0"),
        availability="Out of Stock", ai_summary="", review_summary="",
    )
    db.add(product)
    db.commit()
    try:
        public_products = ProductService(ProductRepository(db)).list_products([product.slug])
        assert product.slug not in {item.id for item in public_products}
    finally:
        db.delete(product)
        db.delete(brand)
        db.delete(category)
        db.commit()
        db.close()
