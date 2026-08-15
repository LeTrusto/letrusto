import asyncio
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_admin_product_service, get_current_admin
from app.core.exceptions import BadRequestError
from app.db.session import SessionLocal
from app.main import app
from app.models.entities import Product, ProductVariant
from app.services.admin_product_service import AdminProductService
from app.suppliers.base import InventorySnapshot, RawSupplierProduct


class SyncAdapter:
    supplier_name = "cj"

    def __init__(self, *, product_exists=True, snapshots=None, failure=None):
        self.product_exists = product_exists
        self.snapshots = snapshots or {}
        self.failure = failure
        self.product_ids = []
        self.product_strict = []
        self.variant_ids = []

    async def authenticate(self) -> bool:
        return True

    async def get_product(self, product_id: str, *, strict: bool = False) -> RawSupplierProduct | None:
        self.product_ids.append(product_id)
        self.product_strict.append(strict)
        if self.failure:
            raise self.failure
        return RawSupplierProduct(supplier_id="cj", supplier_product_id=product_id, supplier_sku="stored", title="Stored") if self.product_exists else None

    async def get_inventory(self, variant_id: str, *, strict: bool = False) -> InventorySnapshot | None:
        self.variant_ids.append(variant_id)
        if self.failure:
            raise self.failure
        return self.snapshots.get(variant_id)


def make_product(db, *, supplier="cj", supplier_product_id="cj-product"):
    product = Product(
        id=uuid4(), slug=f"sync-{uuid4()}", name="Sync product", description="Preserve me",
        status="PAUSED", supplier=supplier, supplier_product_id=supplier_product_id,
        supplier_cost=12, selling_price=40, cj_inventory=9, factory_inventory=8,
    )
    variants = [
        ProductVariant(product_id=product.id, supplier_variant_id="VID-1", supplier_variant_sku="SKU-1", name="One", position=1, total_inventory=17, cj_inventory=9, factory_inventory=8),
        ProductVariant(product_id=product.id, supplier_variant_id="VID-2", supplier_variant_sku="SKU-2", name="Two", position=2, total_inventory=3, cj_inventory=2, factory_inventory=1),
    ]
    db.add_all([product, *variants])
    db.commit()
    return product


def test_sync_maps_stored_vids_separates_factory_and_preserves_metadata(monkeypatch):
    import app.services.admin_product_service as module

    adapter = SyncAdapter(snapshots={
        "VID-1": InventorySnapshot(100, 25, 75, "unverified"),
        "VID-2": InventorySnapshot(40, 10, 30, "verified"),
    })
    def build_adapter(supplier):
        if supplier == "unknown":
            raise ValueError("Unknown supplier provider: unknown")
        return adapter

    monkeypatch.setattr(module, "build_supplier_adapter", build_adapter)
    db = SessionLocal()
    product = make_product(db)
    try:
        before = db.get(Product, product.id)
        result = asyncio.run(AdminProductService(db).sync_inventory(product.id))
        assert adapter.variant_ids == ["VID-1", "VID-2"]
        assert adapter.product_ids == [product.supplier_product_id]
        assert adapter.product_strict == [True]
        assert "SKU-1" not in adapter.product_ids
        assert "SKU-2" not in adapter.product_ids
        assert result.total_inventory == 140
        assert result.cj_inventory == 35
        assert result.factory_inventory == 105
        assert result.verified_warehouse == "verified"
        assert result.status == "PAUSED"
        assert result.supplier_cost == before.supplier_cost
        assert result.selling_price == before.selling_price
        assert result.last_supplier_sync_at is not None
        assert db.get(Product, product.id).last_supplier_sync_at is not None
        assert result.variants[0].cj_inventory == 25
        assert result.variants[0].factory_inventory == 75
        first_sync = result.last_supplier_sync_at
        result = asyncio.run(AdminProductService(db).sync_inventory(product.id))
        assert result.id == product.id
        assert result.last_supplier_sync_at >= first_sync
        assert adapter.product_ids == [product.supplier_product_id, product.supplier_product_id]
        assert adapter.product_strict == [True, True]
    finally:
        db.query(Product).filter(Product.id == product.id).delete(synchronize_session=False)
        db.commit()
        db.close()


@pytest.mark.parametrize(
    "supplier,product_exists,failure,snapshots,expected",
    [
        (None, True, None, {}, "no supplier"),
        ("unknown", True, None, {}, "Unknown supplier provider"),
        ("cj", True, httpx.HTTPError("down"), {}, "synchronization failed"),
        ("cj", True, None, {"VID-1": None, "VID-2": InventorySnapshot(1, 1, 0)}, "Inventory unavailable"),
        ("cj", True, None, {"VID-1": InventorySnapshot(True, 1, 0), "VID-2": InventorySnapshot(1, 1, 0)}, "Malformed inventory"),
        ("cj", False, None, {}, "Supplier product not found"),
    ],
)
def test_sync_failures_do_not_mutate_or_set_timestamp(monkeypatch, supplier, product_exists, failure, snapshots, expected):
    import app.services.admin_product_service as module

    adapter = SyncAdapter(product_exists=product_exists, snapshots=snapshots, failure=failure)
    def build_adapter(provider):
        if provider == "unknown":
            raise ValueError("Unknown supplier provider: unknown")
        return adapter

    monkeypatch.setattr(module, "build_supplier_adapter", build_adapter)
    db = SessionLocal()
    product = make_product(db, supplier=supplier)
    try:
        original = (product.total_inventory, product.cj_inventory, product.factory_inventory, product.last_supplier_sync_at)
        with pytest.raises((BadRequestError, Exception), match=expected):
            asyncio.run(AdminProductService(db).sync_inventory(product.id))
        db.refresh(product)
        assert (product.total_inventory, product.cj_inventory, product.factory_inventory, product.last_supplier_sync_at) == original
    finally:
        db.query(Product).filter(Product.id == product.id).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_sync_route_requires_admin_and_reaches_service(monkeypatch):
    import app.services.admin_product_service as module

    adapter = SyncAdapter(snapshots={"VID-1": InventorySnapshot(1, 1, 0), "VID-2": InventorySnapshot(2, 2, 0)})
    monkeypatch.setattr(module, "build_supplier_adapter", lambda _: adapter)
    db = SessionLocal()
    product = make_product(db)
    service = AdminProductService(db)
    app.dependency_overrides[get_current_admin] = lambda: object()
    app.dependency_overrides[get_admin_product_service] = lambda: service
    try:
        response = TestClient(app).post(f"/api/v1/admin/products/{product.id}/sync-inventory")
        assert response.status_code == 200
        assert response.json()["cj_inventory"] == 3
    finally:
        app.dependency_overrides.clear()
        db.query(Product).filter(Product.id == product.id).delete(synchronize_session=False)
        db.commit()
        db.close()
