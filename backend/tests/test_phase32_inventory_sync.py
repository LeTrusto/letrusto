import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_admin_product_service, get_current_admin, get_current_user
from app.core.exceptions import BadRequestError
from app.db.session import SessionLocal
from app.main import app
from app.models.entities import Product, ProductVariant, SupplierVariantInventory
from app.services.admin_product_service import AdminProductService
from app.services.fulfillment_preflight_service import FulfillmentPreflightService
from app.suppliers.base import InventorySnapshot, RawSupplierProduct, ShippingOption, ShippingResult, ShippingValidation, WarehouseInventorySnapshot


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

    async def calculate_shipping(self, *args, **kwargs) -> ShippingResult:
        return ShippingResult(
            can_ship=True,
            validation=ShippingValidation.VERIFIED,
            options=[ShippingOption(carrier="CJPacket", method="Standard", cost_usd=3.0, estimated_days="8-12")],
            origin_country="CN",
            destination_country="IN",
        )


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


def test_sync_persists_exact_cj_warehouse_identity_without_variant_overwrite(monkeypatch):
    import app.services.admin_product_service as module

    adapter = SyncAdapter(snapshots={
        "E821D001-A0D1-41C3-B492-244A482BD63E": InventorySnapshot(
            53967,
            4,
            53963,
            "verified",
            [WarehouseInventorySnapshot("CN", "1", "China Warehouse", 53967, 4, 53963, "verified")],
        ),
        "VID-OTHER": InventorySnapshot(
            12,
            7,
            5,
            "unverified",
            [WarehouseInventorySnapshot("US", "2", "US Warehouse", 12, 7, 5, "unverified")],
        ),
    })
    monkeypatch.setattr(module, "build_supplier_adapter", lambda _: adapter)
    db = SessionLocal()
    product = make_product(db)
    variants = db.query(ProductVariant).filter(ProductVariant.product_id == product.id).order_by(ProductVariant.position).all()
    variants[0].supplier_variant_id = "E821D001-A0D1-41C3-B492-244A482BD63E"
    variants[1].supplier_variant_id = "VID-OTHER"
    db.commit()
    try:
        asyncio.run(AdminProductService(db).sync_inventory(product.id))
        row = db.query(SupplierVariantInventory).filter(
            SupplierVariantInventory.variant_id == variants[0].id,
        ).one()
        assert row.supplier_variant_id == "E821D001-A0D1-41C3-B492-244A482BD63E"
        assert row.storage_id == "1"
        assert row.warehouse_name == "China Warehouse"
        assert row.warehouse_country == "CN"
        assert row.cj_sellable_inventory == 4
        assert row.factory_inventory == 53963
        assert db.query(SupplierVariantInventory).filter(
            SupplierVariantInventory.variant_id == variants[1].id,
        ).one().supplier_variant_id == "VID-OTHER"

        asyncio.run(AdminProductService(db).sync_inventory(product.id))
        assert db.query(SupplierVariantInventory).filter(
            SupplierVariantInventory.product_id == product.id,
        ).count() == 2
        assert adapter.variant_ids == [
            "E821D001-A0D1-41C3-B492-244A482BD63E",
            "VID-OTHER",
            "E821D001-A0D1-41C3-B492-244A482BD63E",
            "VID-OTHER",
        ]
    finally:
        db.query(Product).filter(Product.id == product.id).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_sync_preserves_existing_identity_when_fresh_inventory_omits_it_and_preflight_consumes_row(monkeypatch):
    import app.services.admin_product_service as module

    adapter = SyncAdapter(snapshots={
        "VID-1": InventorySnapshot(
            80,
            20,
            60,
            "verified",
            [WarehouseInventorySnapshot("CN", None, None, 80, 20, 60, "verified")],
        ),
        "VID-2": InventorySnapshot(0, 0, 0, "verified"),
    })
    monkeypatch.setattr(module, "build_supplier_adapter", lambda _: adapter)
    db = SessionLocal()
    product = make_product(db)
    product.status = "ACTIVE"
    variants = db.query(ProductVariant).filter(ProductVariant.product_id == product.id).order_by(ProductVariant.position).all()
    variants[0].active = True
    variants[1].active = True
    db.add(SupplierVariantInventory(
        product_id=product.id,
        variant_id=variants[0].id,
        supplier="cj",
        supplier_product_id=product.supplier_product_id,
        supplier_variant_id="VID-1",
        warehouse_identity="1",
        warehouse_country="CN",
        storage_id="1",
        warehouse_name="China Warehouse",
        total_inventory=10,
        cj_sellable_inventory=2,
        factory_inventory=8,
        verification_status="verified",
    ))
    db.commit()
    try:
        asyncio.run(AdminProductService(db).sync_inventory(product.id))
        row = db.query(SupplierVariantInventory).filter(SupplierVariantInventory.variant_id == variants[0].id).one()
        assert (row.warehouse_identity, row.storage_id, row.warehouse_name, row.warehouse_country) == ("1", "1", "China Warehouse", "CN")
        assert (row.cj_sellable_inventory, row.factory_inventory) == (20, 60)

        result = asyncio.run(FulfillmentPreflightService(db, adapter).check(
            product_id=product.id,
            variant_id=variants[0].id,
            quantity=1,
            destination_country="IN",
        ))
        assert result.status == "FULFILLABLE"
        assert (result.storage_id, result.warehouse_name, result.sellable_inventory) == ("1", "China Warehouse", 20)
    finally:
        db.query(Product).filter(Product.id == product.id).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_admin_inventory_route_returns_all_warehouse_rows_without_mutation():
    db = SessionLocal()
    product = make_product(db)
    variants = db.query(ProductVariant).filter(ProductVariant.product_id == product.id).order_by(ProductVariant.position).all()
    first_sync = datetime.now(timezone.utc)
    rows = [
        SupplierVariantInventory(
            product_id=product.id, variant_id=variants[0].id, supplier="cj", supplier_product_id=product.supplier_product_id,
            supplier_variant_id="VID-1", warehouse_identity="1", warehouse_country="CN", storage_id="1",
            warehouse_name="China Warehouse", total_inventory=80, cj_sellable_inventory=20, factory_inventory=60,
            last_synced_at=first_sync,
        ),
        SupplierVariantInventory(
            product_id=product.id, variant_id=variants[0].id, supplier="cj", supplier_product_id=product.supplier_product_id,
            supplier_variant_id="VID-1", warehouse_identity="2", warehouse_country="US", storage_id="2",
            warehouse_name="US Warehouse", total_inventory=40, cj_sellable_inventory=10, factory_inventory=30,
            last_synced_at=first_sync,
        ),
    ]
    db.add_all(rows)
    db.commit()
    before = [(row.id, row.last_synced_at, row.cj_sellable_inventory, row.factory_inventory) for row in rows]
    service = AdminProductService(db)
    app.dependency_overrides[get_current_admin] = lambda: object()
    app.dependency_overrides[get_admin_product_service] = lambda: service
    try:
        response = TestClient(app).get(f"/api/v1/admin/products/{product.id}/inventory")
        assert response.status_code == 200
        payload = response.json()
        assert payload["product_id"] == str(product.id)
        first = payload["variants"][0]
        assert (first["vid"], first["sku"]) == ("VID-1", "SKU-1")
        assert (first["sellable_cj_inventory"], first["factory_inventory"], first["total_inventory"]) == (9, 8, 17)
        assert [(row["warehouse_country"], row["warehouse_name"], row["storage_id"], row["sellable_cj_inventory"], row["factory_inventory"]) for row in first["warehouses"]] == [
            ("CN", "China Warehouse", "1", 20, 60),
            ("US", "US Warehouse", "2", 10, 30),
        ]
        assert all(row["last_synced_at"] for row in first["warehouses"])
        db.expire_all()
        after = [(row.id, row.last_synced_at, row.cj_sellable_inventory, row.factory_inventory) for row in db.query(SupplierVariantInventory).filter(SupplierVariantInventory.product_id == product.id).order_by(SupplierVariantInventory.storage_id)]
        expected = sorted(before, key=lambda item: next(row.storage_id for row in rows if row.id == item[0]))
        assert after == expected
    finally:
        app.dependency_overrides.clear()
        db.query(Product).filter(Product.id == product.id).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_admin_inventory_route_rejects_unauthenticated_and_customer_users():
    db = SessionLocal()
    product = make_product(db)
    try:
        unauthenticated = TestClient(app).get(f"/api/v1/admin/products/{product.id}/inventory")
        assert unauthenticated.status_code == 401
        app.dependency_overrides[get_current_user] = lambda: type("Customer", (), {"role": "customer"})()
        customer = TestClient(app).get(f"/api/v1/admin/products/{product.id}/inventory")
        assert customer.status_code == 401
    finally:
        app.dependency_overrides.clear()
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
