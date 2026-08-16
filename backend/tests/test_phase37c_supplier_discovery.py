from __future__ import annotations

import asyncio
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api.deps import get_current_admin
from app.db.session import SessionLocal
from app.main import app
from app.models.entities import Product, SupplierCandidate, User
from app.services.launch_pricing_policy import load_launch_pricing_policy
from app.services.supplier_discovery_service import (
    SupplierAuthenticationError,
    SupplierDiscoveryService,
)
from app.suppliers.base import (
    RawSupplierProduct,
    RawVariant,
    ShippingOption,
    ShippingResult,
    ShippingValidation,
)


class DiscoveryAdapter:
    supplier_name = "cj"

    def __init__(self, count: int = 20) -> None:
        self.authenticated = True
        self.search_calls: list[tuple] = []
        self.detail_calls: list[tuple] = []
        self.shipping_calls: list[tuple] = []
        self.shipping_failure_id: str | None = None
        self.items = [self._product(index, detail=False) for index in range(count)]

    async def authenticate(self) -> bool:
        return self.authenticated

    async def search_products(self, keyword: str, **kwargs):
        self.search_calls.append((keyword, kwargs))
        return self.items

    async def get_product(self, product_id: str, *, strict: bool = False):
        self.detail_calls.append((product_id, strict))
        index = int(product_id.split("-")[-1])
        return self._product(index, detail=True)

    async def calculate_shipping(self, variant_id: str, destination: str, **kwargs):
        self.shipping_calls.append((variant_id, destination, kwargs))
        if variant_id == self.shipping_failure_id:
            raise RuntimeError("transient freight failure")
        return ShippingResult(
            can_ship=True,
            validation=ShippingValidation.VERIFIED,
            options=[ShippingOption(
                carrier="CJPacket",
                method="Standard",
                cost_usd=2.0,
                estimated_days="8-12",
            )],
            origin_country="CN",
            destination_country=destination,
        )

    @staticmethod
    def _product(index: int, *, detail: bool) -> RawSupplierProduct:
        product_id = f"PID-{index:02d}"
        variants = []
        if detail:
            variants = [
                RawVariant(
                    supplier_variant_id=f"VID-{index:02d}-A",
                    supplier_variant_sku=f"VSKU-{index:02d}-A",
                    name="Black",
                    option_key="Color-Black",
                    price_usd=2.0 + index / 10,
                    weight_grams=25.0,
                    total_inventory=1000 + index,
                    cj_inventory=100 + index,
                    factory_inventory=900,
                    inventory_verification="verified",
                ),
                RawVariant(
                    supplier_variant_id=f"VID-{index:02d}-B",
                    supplier_variant_sku=f"VSKU-{index:02d}-B",
                    name="Gold",
                    option_key="Color-Gold",
                    price_usd=3.0 + index / 10,
                    weight_grams=30.0,
                    total_inventory=2000 + index,
                    cj_inventory=200 + index,
                    factory_inventory=1800,
                    inventory_verification="verified",
                ),
            ]
        return RawSupplierProduct(
            supplier_id="cj",
            supplier_product_id=product_id,
            supplier_sku=f"SKU-{index:02d}",
            title=f"Hair Clip {index:02d}",
            description="Complete supplier detail",
            images=[f"https://example.com/{index}.jpg"],
            category_name="Hair Accessories",
            price_usd=2.0 + index / 10,
            weight_grams=25.0,
            variants=variants,
            inventory_total=300 + index * 2,
            total_inventory=3000 + index * 2,
            cj_inventory=300 + index * 2,
            factory_inventory=2700,
            inventory_verification="verified",
            warehouse_country="CN",
        )


def run_discovery(adapter: DiscoveryAdapter, page_size: int = 20):
    return asyncio.run(SupplierDiscoveryService(adapter).discover("hair clip", "IN", page_size))


def test_discovery_processes_twenty_with_exactly_one_search_detail_and_shipping_each():
    adapter = DiscoveryAdapter()
    result = run_discovery(adapter)

    assert result.returned_count == result.success_count == 20
    assert result.failed_count == 0
    assert adapter.search_calls == [("hair clip", {"page_size": 20})]
    assert adapter.detail_calls == [(f"PID-{index:02d}", True) for index in range(20)]
    assert len(adapter.shipping_calls) == 20
    assert all(call[0].endswith("-A") for call in adapter.shipping_calls)


def test_discovery_maps_canonical_variants_inventory_and_exact_launch_pricing():
    result = run_discovery(DiscoveryAdapter(count=1), page_size=1)
    product = result.products[0]
    first = product.variants[0]

    assert product.canonical_product_id == "PID-00"
    assert product.supplier_sku == "SKU-00"
    assert (product.total_inventory, product.cj_inventory, product.factory_inventory) == (3000, 300, 2700)
    assert (first.supplier_variant_id, first.supplier_variant_sku) == ("VID-00-A", "VSKU-00-A")
    assert (first.total_inventory, first.cj_inventory, first.factory_inventory) == (1000, 100, 900)
    assert first.phase2_cost_inr == 167.0
    assert first.launch_cost_inr == Decimal("196.0")
    assert product.shipping_options[0].cost_inr == Decimal("196.0")
    assert first.pricing.selling_price_inr == Decimal("532.32")
    assert first.pricing.contribution_before_cac_inr == Decimal("106.47")
    assert first.pricing.contribution_after_target_cac_inr == Decimal("-43.53")
    assert product.shipping_based_on_variant_id == "VID-00-A"
    assert product.shipping_applied_to_all_variants is True


def test_discovery_reuses_phase2_normalize_economics_and_scoring(monkeypatch):
    import app.services.supplier_discovery_service as module

    calls = {"normalize": 0, "economics": 0, "score": 0}
    real_normalize = module.normalize_product
    real_economics = module.calculate_economics
    real_score = module.score_product

    def normalize_spy(*args, **kwargs):
        calls["normalize"] += 1
        assert kwargs["usd_to_inr"] == 83.5
        return real_normalize(*args, **kwargs)

    def economics_spy(*args, **kwargs):
        calls["economics"] += 1
        assert kwargs["config"].usd_to_inr == 83.5
        return real_economics(*args, **kwargs)

    def score_spy(*args, **kwargs):
        calls["score"] += 1
        return real_score(*args, **kwargs)

    monkeypatch.setattr(module, "normalize_product", normalize_spy)
    monkeypatch.setattr(module, "calculate_economics", economics_spy)
    monkeypatch.setattr(module, "score_product", score_spy)
    run_discovery(DiscoveryAdapter(count=2), page_size=2)
    assert calls == {"normalize": 2, "economics": 2, "score": 2}


def test_discovery_isolates_transient_failure_and_marks_market_insufficient():
    adapter = DiscoveryAdapter(count=3)
    adapter.shipping_failure_id = "VID-01-A"
    result = run_discovery(adapter, page_size=3)

    assert (result.returned_count, result.success_count, result.failed_count) == (3, 2, 1)
    assert result.failures[0].requested_product_id == "PID-01"
    assert result.failures[0].stage == "SHIPPING"
    assert result.failures[0].recommendation == "REVIEW"
    assert result.verdict_counts.review >= 1
    assert all(product.market_status == "INSUFFICIENT_MARKET_DATA" for product in result.products)


def test_discovery_ranking_priorities_and_top_three_are_deterministic():
    result = run_discovery(DiscoveryAdapter(count=4), page_size=4)
    products = result.products
    products[0].canonical_product_id = "D"
    products[1].canonical_product_id = "C"
    products[2].canonical_product_id = "B"
    products[3].canonical_product_id = "A"
    products[0].ranking_factors.all_priced_variants_positive_before_cac = False
    products[1].ranking_factors.all_priced_variants_support_cac = True
    products[1].ranking_factors.cac_supported_variant_count = 2
    products[2].ranking_factors.supplier_score += 1
    products[3].ranking_factors.supplier_score += 1
    products[3].ranking_factors.cj_inventory = products[2].ranking_factors.cj_inventory

    ranked = sorted(products, key=SupplierDiscoveryService._sort_key)
    assert [product.canonical_product_id for product in ranked] == ["C", "A", "B", "D"]
    assert len(result.top_recommendations) == 3
    assert [product.rank for product in result.products] == [1, 2, 3, 4]


def test_discovery_uses_approved_launch_policy_and_commercial_mapping():
    policy = load_launch_pricing_policy()
    assert (
        policy.pricing_fx_rate,
        policy.payment_gateway_pct,
        policy.rto_reserve_pct,
        policy.target_contribution_margin_pct,
        policy.target_cac_inr,
    ) == (Decimal("98"), Decimal("2.36"), Decimal("4"), Decimal("20"), Decimal("150"))
    product = run_discovery(DiscoveryAdapter(count=1), page_size=1).products[0]
    assert product.phase2_verdict in {"PASS", "REVIEW", "REJECT"}
    assert product.commercial_review.decision in {"APPROVED", "REVIEW", "REJECTED"}
    assert product.recommendation in {"APPROVED_CANDIDATE", "REVIEW", "REJECTED"}
    assert "CAC_TARGET_NOT_SUPPORTED" in product.commercial_review.reasons


def test_discovery_authentication_failure_aborts_before_search():
    adapter = DiscoveryAdapter(count=1)
    adapter.authenticated = False
    with pytest.raises(SupplierAuthenticationError, match="authentication"):
        run_discovery(adapter, page_size=1)
    assert adapter.search_calls == []


def test_discovery_does_not_mutate_products_or_candidates():
    with SessionLocal() as db:
        before = (
            db.scalar(select(func.count()).select_from(Product)),
            db.scalar(select(func.count()).select_from(SupplierCandidate)),
        )
    run_discovery(DiscoveryAdapter(count=2), page_size=2)
    with SessionLocal() as db:
        after = (
            db.scalar(select(func.count()).select_from(Product)),
            db.scalar(select(func.count()).select_from(SupplierCandidate)),
        )
    assert after == before


def test_discovery_endpoint_requires_admin_authentication():
    response = TestClient(app).get(
        "/api/v1/admin/supplier-discovery",
        params={"keyword": "hair clip", "destination": "IN", "page_size": 20},
    )
    assert response.status_code == 401


def test_discovery_endpoint_returns_orchestration_response(monkeypatch):
    import app.api.v1.endpoints.supplier_discovery as endpoint

    adapter = DiscoveryAdapter(count=2)
    admin = User(email="discovery-admin@example.com", full_name="Discovery Admin", role="admin")
    app.dependency_overrides[get_current_admin] = lambda: admin
    monkeypatch.setattr(endpoint, "build_supplier_adapter", lambda *_: adapter)
    try:
        response = TestClient(app).get(
            "/api/v1/admin/supplier-discovery",
            params={"keyword": "hair clip", "destination": "IN", "page_size": 2},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "hair clip"
    assert body["returned_count"] == 2
    assert len(body["products"]) == 2
    assert adapter.search_calls == [("hair clip", {"page_size": 2})]