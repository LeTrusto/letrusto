"""Tests for supplier adapter, normalizer, economics, and scoring — Phase 2."""

import asyncio
import httpx
import pytest
from unittest.mock import AsyncMock

from app.suppliers.base import (
    RawSupplierProduct,
    RawVariant,
    ShippingOption,
    ShippingResult,
    ShippingValidation,
)
from app.suppliers.economics import (
    CostStatus,
    EconomicsConfig,
    MarginStatus,
    calculate_economics,
)
from app.suppliers.normalizer import (
    NormalizedProduct,
    ProductStatus,
    normalize_product,
)
from app.suppliers.scoring import (
    ProductScore,
    ScoreThresholds,
    ScoreVerdict,
    score_product,
)


# ── Fixtures ─────────────────────────────────────────


def _make_raw(
    *,
    price_usd: float | None = 5.0,
    weight: float | None = 200.0,
    inventory: int | None = 500,
    title: str = "Pearl Hair Clip Set",
    images: list[str] | None = None,
    category: str = "Hair Accessories",
    variants: list[RawVariant] | None = None,
) -> RawSupplierProduct:
    return RawSupplierProduct(
        supplier_id="cj",
        supplier_product_id="PROD-001",
        supplier_sku="CJTEST001",
        title=title,
        description="A test product for validation",
        images=["https://example.com/img.jpg"] if images is None else images,
        category_name=category,
        category_id="CAT-001",
        price_usd=price_usd,
        weight_grams=weight,
        inventory_total=inventory,
        warehouse_country="CN",
        delivery_cycle_days="3-5",
        variants=variants or [],
    )


def _make_shipping(
    *, can_ship: bool = True, cost_usd: float = 3.5, days: str = "10-15"
) -> ShippingResult:
    if not can_ship:
        return ShippingResult(
            can_ship=False,
            validation=ShippingValidation.NOT_AVAILABLE,
            origin_country="CN",
            destination_country="IN",
        )
    return ShippingResult(
        can_ship=True,
        validation=ShippingValidation.VERIFIED,
        options=[ShippingOption(carrier="CJPacket", method="CJPacket", cost_usd=cost_usd, estimated_days=days)],
        origin_country="CN",
        destination_country="IN",
    )


# ── Normalizer Tests ─────────────────────────────────


class TestNormalizer:
    def test_normalize_complete_product(self) -> None:
        raw = _make_raw()
        normalized = normalize_product(raw)

        assert normalized.status == ProductStatus.NORMALIZED
        assert normalized.supplier_id == "cj"
        assert normalized.supplier_sku == "CJTEST001"
        assert normalized.cost_usd == 5.0
        assert normalized.cost_inr is not None
        assert normalized.cost_inr > 0
        assert normalized.missing_fields == []

    def test_normalize_missing_price(self) -> None:
        raw = _make_raw(price_usd=None)
        normalized = normalize_product(raw)

        assert "price" in normalized.missing_fields
        assert normalized.cost_inr is None

    def test_normalize_missing_images(self) -> None:
        raw = _make_raw(images=[])
        normalized = normalize_product(raw)

        assert "images" in normalized.missing_fields

    def test_normalize_missing_weight(self) -> None:
        raw = _make_raw(weight=None)
        normalized = normalize_product(raw)

        assert "weight" in normalized.missing_fields

    def test_normalize_missing_inventory(self) -> None:
        raw = _make_raw(inventory=None)
        normalized = normalize_product(raw)

        assert "inventory" in normalized.missing_fields

    def test_normalize_missing_category(self) -> None:
        raw = _make_raw(category="")
        normalized = normalize_product(raw)

        assert "category" in normalized.missing_fields

    def test_normalize_missing_title(self) -> None:
        raw = _make_raw(title="")
        normalized = normalize_product(raw)

        assert "title" in normalized.missing_fields

    def test_normalize_custom_exchange_rate(self) -> None:
        raw = _make_raw(price_usd=10.0)
        normalized = normalize_product(raw, usd_to_inr=85.0)

        assert normalized.cost_inr == 850.0

    def test_normalize_variants(self) -> None:
        variants = [
            RawVariant(
                supplier_variant_id="V001",
                supplier_variant_sku="CJTEST001-Red",
                name="Red",
                option_key="Red-M",
                price_usd=5.5,
                weight_grams=210.0,
                inventory=100,
                warehouse_country="CN",
            ),
        ]
        raw = _make_raw(variants=variants)
        normalized = normalize_product(raw)

        assert len(normalized.variants) == 1
        assert normalized.variants[0].supplier_variant_sku == "CJTEST001-Red"
        assert normalized.variants[0].cost_inr is not None

    def test_letrusto_product_id_format(self) -> None:
        raw = _make_raw()
        normalized = normalize_product(raw)

        assert normalized.letrusto_product_id.startswith("lt-cj-")


# ── Economics Tests ──────────────────────────────────


class TestEconomics:
    def test_full_economics_with_shipping(self) -> None:
        raw = _make_raw(price_usd=5.0)
        normalized = normalize_product(raw)
        economics = calculate_economics(normalized, shipping_cost_usd=3.5)

        assert economics.supplier_cost_inr.status == CostStatus.KNOWN
        assert economics.shipping_cost_inr.status == CostStatus.KNOWN
        assert economics.selling_price_inr is not None
        assert economics.contribution_inr is not None
        assert economics.contribution_pct is not None

    def test_economics_without_shipping(self) -> None:
        raw = _make_raw(price_usd=5.0)
        normalized = normalize_product(raw)
        economics = calculate_economics(normalized, shipping_cost_usd=None)

        assert "shipping_cost" in economics.unknown_costs
        assert economics.margin_status == MarginStatus.UNKNOWN

    def test_economics_without_supplier_cost(self) -> None:
        raw = _make_raw(price_usd=None)
        normalized = normalize_product(raw)
        economics = calculate_economics(normalized)

        assert "supplier_cost" in economics.unknown_costs
        assert economics.selling_price_inr is None

    def test_economics_rto_unknown_by_default(self) -> None:
        raw = _make_raw(price_usd=5.0)
        normalized = normalize_product(raw)
        economics = calculate_economics(normalized, shipping_cost_usd=3.0)

        assert "rto_reserve" in economics.unknown_costs

    def test_economics_custom_config(self) -> None:
        raw = _make_raw(price_usd=5.0)
        normalized = normalize_product(raw)
        config = EconomicsConfig(
            payment_fee_pct=0.03,
            rto_reserve_pct=0.08,
            creator_commission_pct=0.15,
            marketing_allowance_pct=0.10,
            target_markup=3.0,
        )
        economics = calculate_economics(normalized, shipping_cost_usd=3.0, config=config)

        assert "rto_reserve" not in economics.unknown_costs
        assert economics.rto_reserve_inr.status == CostStatus.ESTIMATED

    def test_selling_price_rounds_to_price_point(self) -> None:
        raw = _make_raw(price_usd=5.0)
        normalized = normalize_product(raw)
        economics = calculate_economics(normalized, shipping_cost_usd=3.0)

        if economics.selling_price_inr is not None:
            remainder = economics.selling_price_inr % 100
            assert remainder in (49, 99) or economics.selling_price_inr == 99


# ── Scoring Tests ────────────────────────────────────


class TestScoring:
    def test_good_product_passes(self) -> None:
        raw = _make_raw(price_usd=5.0, inventory=600)
        normalized = normalize_product(raw)
        shipping = _make_shipping(cost_usd=3.0)
        economics = calculate_economics(normalized, shipping_cost_usd=3.0)
        score = score_product(normalized, economics=economics, shipping=shipping)

        assert score.score > 0
        assert score.verdict in (ScoreVerdict.PASS, ScoreVerdict.REVIEW)

    def test_no_shipping_lowers_score(self) -> None:
        raw = _make_raw(price_usd=5.0)
        normalized = normalize_product(raw)
        score_with = score_product(normalized, shipping=_make_shipping())
        score_without = score_product(normalized, shipping=None)

        assert score_with.score > score_without.score

    def test_unprofitable_product(self) -> None:
        raw = _make_raw(price_usd=5.0, inventory=5)
        normalized = normalize_product(raw)
        shipping = _make_shipping(can_ship=False)
        economics = calculate_economics(normalized, shipping_cost_usd=None)
        score = score_product(normalized, economics=economics, shipping=shipping)

        # Low inventory, no shipping, unknown margin — should score low
        assert score.verdict in (ScoreVerdict.REVIEW, ScoreVerdict.REJECT)

    def test_missing_data_reduces_completeness(self) -> None:
        raw = _make_raw(price_usd=None, weight=None, images=[], inventory=None, category="")
        normalized = normalize_product(raw)
        score = score_product(normalized)

        # 5 missing fields * 2 = 10, so 10 - 10 = 0
        assert score.breakdown.data_completeness == 0
        assert "Missing:" in " ".join(score.notes)

    def test_custom_thresholds(self) -> None:
        raw = _make_raw()
        normalized = normalize_product(raw)
        thresholds = ScoreThresholds(pass_threshold=90, review_threshold=80)
        score = score_product(normalized, thresholds=thresholds)

        # With very high thresholds, most products won't pass
        assert score.score < 90 or score.verdict == ScoreVerdict.PASS

    def test_heavy_product_reduces_return_risk_score(self) -> None:
        light = _make_raw(weight=200.0)
        heavy = _make_raw(weight=3000.0)
        score_light = score_product(normalize_product(light))
        score_heavy = score_product(normalize_product(heavy))

        assert score_light.breakdown.return_risk > score_heavy.breakdown.return_risk

    def test_restricted_logistics_reduces_score(self) -> None:
        raw = _make_raw()
        raw.logistics_properties = ["BATTERY"]
        normalized = normalize_product(raw)
        score = score_product(normalized)

        assert score.breakdown.return_risk < 8

    def test_score_without_economics_or_shipping(self) -> None:
        raw = _make_raw()
        normalized = normalize_product(raw)
        score = score_product(normalized, economics=None, shipping=None)

        assert score.score >= 0
        assert "Shipping not validated" in score.notes
        assert "Economics not calculated" in score.notes


# ── Adapter Protocol Tests ───────────────────────────


class TestAdapterProtocol:
    def test_cj_adapter_implements_protocol(self) -> None:
        from app.suppliers.adapters.cj_adapter import CJAdapter
        from app.suppliers.base import SupplierAdapter

        adapter = CJAdapter(api_key="test-key")
        assert isinstance(adapter, SupplierAdapter)
        assert adapter.supplier_name == "cj"


# ── CJ Response Parsing Tests ───────────────────────


class TestCJParsing:
    def test_parse_list_product(self) -> None:
        from app.suppliers.adapters.cj_adapter import CJAdapter

        adapter = CJAdapter(api_key="test")
        item = {
            "id": "PROD-123",
            "nameEn": "Test Earrings",
            "sku": "CJTEST123",
            "spu": "CJTEST123",
            "bigImage": "https://example.com/img.jpg",
            "sellPrice": "4.50",
            "warehouseInventoryNum": 250,
            "categoryId": "CAT-1",
            "threeCategoryName": "Earrings",
            "deliveryCycle": "3-5",
        }
        raw = adapter._parse_list_product(item)

        assert raw.supplier_product_id == "PROD-123"
        assert raw.title == "Test Earrings"
        assert raw.price_usd == 4.5
        assert raw.inventory_total == 250

    def test_get_product_resolves_supplier_sku_after_direct_404(self) -> None:
        from app.suppliers.adapters.cj_adapter import CJAdapter

        adapter = CJAdapter(api_key="test")
        not_found = httpx.HTTPStatusError(
            "not found",
            request=httpx.Request("GET", "https://example.com/product/query"),
            response=httpx.Response(404),
        )
        adapter._get = AsyncMock(
            side_effect=[
                not_found,
                {
                    "result": True,
                    "data": {
                        "content": [{
                            "productList": [{
                                "id": "PRODUCT-123",
                                "sku": "CJJT2327063",
                                "nameEn": "Test Hair Clip",
                            }]
                        }]
                    },
                },
                {
                    "result": True,
                    "data": {
                        "pid": "PRODUCT-123",
                        "productNameEn": "Test Hair Clip",
                        "productImageSet": ["https://example.com/clip.jpg"],
                        "variants": [{
                            "vid": "VAR-123",
                            "variantSku": "CJJT2327063-RED",
                            "inventories": [{
                                "totalInventory": 40,
                                "cjInventory": 40,
                                "factoryInventory": 77651,
                                "verifiedWarehouse": 1,
                            }],
                        }],
                    },
                },
            ]
        )

        raw = asyncio.run(adapter.get_product("CJJT2327063"))

        assert raw is not None
        assert raw.supplier_product_id == "PRODUCT-123"
        assert raw.cj_inventory == 40
        assert raw.factory_inventory == 77651
        assert raw.variants[0].supplier_variant_sku == "CJJT2327063-RED"

    def test_parse_variant(self) -> None:
        from app.suppliers.adapters.cj_adapter import CJAdapter

        adapter = CJAdapter(api_key="test")
        v = {
            "vid": "VAR-001",
            "variantSku": "CJTEST123-Gold",
            "variantNameEn": "Gold Earrings",
            "variantKey": "Gold",
            "variantSellPrice": 4.50,
            "variantWeight": 30.0,
            "variantLength": 50,
            "variantWidth": 30,
            "variantHeight": 10,
            "inventories": [
                {"countryCode": "CN", "totalInventory": 1000},
            ],
        }
        variant = adapter._parse_variant(v)

        assert variant.supplier_variant_id == "VAR-001"
        assert variant.price_usd == 4.5
        assert variant.inventory == 1000
        assert variant.warehouse_country == "CN"

    def test_parse_variant_no_inventory(self) -> None:
        from app.suppliers.adapters.cj_adapter import CJAdapter

        adapter = CJAdapter(api_key="test")
        v = {"vid": "VAR-002", "variantSku": "CJTEST-X", "inventories": []}
        variant = adapter._parse_variant(v)

        assert variant.inventory == 0

    def test_parse_variant_null_inventory(self) -> None:
        from app.suppliers.adapters.cj_adapter import CJAdapter

        adapter = CJAdapter(api_key="test")
        v = {"vid": "VAR-003", "variantSku": "CJTEST-NULL", "inventories": None}
        variant = adapter._parse_variant(v)

        assert variant.supplier_variant_id == "VAR-003"
        assert variant.supplier_variant_sku == "CJTEST-NULL"
        assert variant.inventory == 0

    def test_get_inventory_maps_cj_and_factory_inventory(self) -> None:
        from app.suppliers.adapters.cj_adapter import CJAdapter

        adapter = CJAdapter(api_key="test")
        adapter._get = AsyncMock(
            return_value={
                "result": True,
                "data": [
                    {
                        "totalInventoryNum": 1500,
                        "cjInventoryNum": 500,
                        "factoryInventoryNum": 1000,
                        "verifiedWarehouse": 1,
                    }
                ],
            }
        )

        snapshot = asyncio.run(adapter.get_inventory("VAR-004"))

        assert snapshot is not None
        assert snapshot.total_inventory == 1500
        assert snapshot.cj_inventory == 500
        assert snapshot.factory_inventory == 1000
        assert snapshot.verification_status == "verified"

    def test_normalize_preserves_source_total_and_scores_cj_inventory(self) -> None:
        from app.suppliers.adapters.cj_adapter import CJAdapter

        adapter = CJAdapter(api_key="test")
        adapter._get = AsyncMock(
            return_value={
                "result": True,
                "data": [
                    {
                        "totalInventoryNum": 1500,
                        "cjInventoryNum": 500,
                        "factoryInventoryNum": 1000,
                    }
                ],
            }
        )

        snapshot = asyncio.run(adapter.get_inventory("VAR-007"))
        raw = _make_raw(
            inventory=snapshot.cj_inventory if snapshot else None,
        )
        raw.total_inventory = snapshot.total_inventory if snapshot else None
        raw.cj_inventory = snapshot.cj_inventory if snapshot else None
        raw.factory_inventory = snapshot.factory_inventory if snapshot else None
        normalized = normalize_product(raw)

        assert normalized.total_inventory == 500
        assert normalized.source_total_inventory == 1500
        assert normalized.factory_inventory == 1000

    def test_get_inventory_factory_only_is_not_sellable(self) -> None:
        from app.suppliers.adapters.cj_adapter import CJAdapter

        adapter = CJAdapter(api_key="test")
        adapter._get = AsyncMock(
            return_value={
                "result": True,
                "data": [
                    {
                        "totalInventoryNum": 40000,
                        "cjInventoryNum": 0,
                        "factoryInventoryNum": 40000,
                        "verifiedWarehouse": 2,
                    }
                ],
            }
        )

        snapshot = asyncio.run(adapter.get_inventory("VAR-005"))

        assert snapshot is not None
        assert snapshot.total_inventory == 40000
        assert snapshot.cj_inventory == 0
        assert snapshot.factory_inventory == 40000
        assert snapshot.verification_status == "unverified"

    @pytest.mark.parametrize(
        "entry",
        [
            {"totalInventoryNum": 0, "cjInventoryNum": 0, "factoryInventoryNum": 0},
            {"totalInventoryNum": None, "cjInventoryNum": None, "factoryInventoryNum": None},
        ],
    )
    def test_get_inventory_zero_or_null_fields_are_safe(self, entry: dict) -> None:
        from app.suppliers.adapters.cj_adapter import CJAdapter

        adapter = CJAdapter(api_key="test")
        adapter._get = AsyncMock(return_value={"result": True, "data": [entry]})

        snapshot = asyncio.run(adapter.get_inventory("VAR-006"))

        assert snapshot is not None
        assert snapshot.cj_inventory == 0
        assert snapshot.factory_inventory == 0


class TestCJAuthentication:
    @pytest.fixture(autouse=True)
    def clear_token_cache(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import app.suppliers.adapters.cj_adapter as cj

        monkeypatch.setattr(cj, "_cached_access_token", "")
        monkeypatch.setattr(cj, "_cached_token_expires_at", 0.0)

    def test_successful_authentication_caches_token(self) -> None:
        from app.suppliers.adapters.cj_adapter import CJAdapter

        adapter = CJAdapter(api_key="fake-key")
        adapter._post = AsyncMock(
            return_value={"result": True, "data": {"accessToken": "fake-token", "accessTokenExpiry": 3600}}
        )

        assert asyncio.run(adapter.authenticate()) is True
        assert adapter._headers()["CJ-Access-Token"] == "fake-token"
        assert adapter._post.await_count == 1
        assert asyncio.run(adapter.authenticate()) is True
        assert adapter._post.await_count == 1

    def test_authentication_failure_is_false(self) -> None:
        from app.suppliers.adapters.cj_adapter import CJAdapter

        adapter = CJAdapter(api_key="fake-key")
        adapter._post = AsyncMock(return_value={"result": False, "data": None, "message": "secret-safe"})

        assert asyncio.run(adapter.authenticate()) is False
        assert "CJ-Access-Token" not in adapter._headers()

    def test_malformed_authentication_response_is_false(self) -> None:
        from app.suppliers.adapters.cj_adapter import CJAdapter

        adapter = CJAdapter(api_key="fake-key")
        adapter._post = AsyncMock(return_value=[])

        assert asyncio.run(adapter.authenticate()) is False

    def test_missing_api_key_is_rejected(self) -> None:
        from app.suppliers.adapters.cj_adapter import CJAdapter

        with pytest.raises(ValueError, match="not configured"):
            CJAdapter(api_key=" ")

    def test_expired_token_reauthenticates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import app.suppliers.adapters.cj_adapter as cj
        from app.suppliers.adapters.cj_adapter import CJAdapter

        monkeypatch.setattr(cj, "_cached_access_token", "expired-token")
        monkeypatch.setattr(cj, "_cached_token_expires_at", 1.0)
        adapter = CJAdapter(api_key="fake-key")
        adapter._post = AsyncMock(
            return_value={"result": True, "data": {"accessToken": "fresh-token", "accessTokenExpiry": 3600}}
        )

        assert asyncio.run(adapter.authenticate()) is True
        assert adapter._headers()["CJ-Access-Token"] == "fresh-token"
        adapter._post.assert_awaited_once()
