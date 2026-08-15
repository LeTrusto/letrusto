import asyncio
from decimal import Decimal
from uuid import UUID, uuid4

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
        assert len(result.images) == 2
        assert result.variants[0].supplier_variant_id == "VID-TEST-001"
        assert result.variants[0].cj_inventory == 50
        assert result.variants[0].factory_inventory == 1000
    finally:
        db.query(Product).filter(Product.supplier_product_id == product_id).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_import_is_idempotent_and_status_updates(monkeypatch):
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

        updated = service.update_status(first.id, ProductStatusUpdate(status="ACTIVE"))
        assert updated.status == "ACTIVE"
        updated = service.update_status(first.id, ProductStatusUpdate(status="PAUSED"))
        assert updated.status == "PAUSED"
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
        default = service.list_products(None, None, False, 0, 100)
        assert all(product.supplier is not None for product in default.products)
        assert supplier.id in {product.id for product in default.products}
        assert legacy.id not in {product.id for product in default.products}

        legacy_only = service.list_products(None, None, True, 0, 1000)
        legacy_ids = {product.id for product in legacy_only.products}
        assert legacy.id in legacy_ids
        assert supplier.id not in legacy_ids
        assert all(product.supplier is None for product in legacy_only.products)

        filtered = service.list_products(None, "cj", False, 0, 100)
        assert {product.id for product in filtered.products} == {supplier.id}
        assert db.get(Product, legacy.id).status == "ACTIVE"
    finally:
        db.delete(supplier)
        db.delete(legacy)
        db.delete(brand)
        db.delete(category)
        db.commit()
        db.close()
