from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.catalog_readiness import CatalogPricingPolicy, is_allowed_image_url, is_inventory_stale, resolve_cj_category, resolve_brand
from app.services.catalog_readiness_service import CatalogReadinessService


def ready_product(**overrides):
    values = {
        "supplier": "cj",
        "supplier_product_id": "CJ-1",
        "name": "Pilot product",
        "description": "Product description",
        "category_id": 25,
        "brand_id": 1,
        "images": [SimpleNamespace(url="https://cf.cjdropshipping.com/quick/product/image.jpg")],
        "variants": [SimpleNamespace(active=True, supplier_variant_id="VID-1", supplier_variant_sku="SKU-1", selling_price=Decimal("499"), cj_inventory=5)],
        "shipping_cost": Decimal("100"),
        "commercial_status": "APPROVED",
        "supplier_validation_status": "PASS",
        "last_supplier_sync_at": datetime.now(timezone.utc),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_activation_readiness_accepts_complete_product():
    result = CatalogReadinessService.validate_activation(ready_product())
    assert result.ready is True
    assert result.blocking_reasons == ()


@pytest.mark.parametrize("field,reason", [("category_id", "CATEGORY_REVIEW_REQUIRED"), ("brand_id", "BRAND_REVIEW_REQUIRED"), ("shipping_cost", "SHIPPING_COST_MISSING")])
def test_activation_readiness_blocks_missing_enrichment(field, reason):
    product = ready_product(**{field: None})
    result = CatalogReadinessService.validate_activation(product)
    assert reason in result.blocking_reasons


def test_activation_readiness_blocks_invalid_image_and_zero_sellable_inventory():
    product = ready_product(
        images=[SimpleNamespace(url="https://example.com/image.jpg")],
        variants=[SimpleNamespace(active=True, supplier_variant_id="VID-1", supplier_variant_sku="SKU-1", selling_price=Decimal("499"), cj_inventory=0)],
    )
    result = CatalogReadinessService.validate_activation(product)
    assert "PRIMARY_IMAGE_INVALID" in result.blocking_reasons
    assert "NO_SELLABLE_INVENTORY" in result.blocking_reasons


def test_category_mapping_is_deterministic_and_unknown_requires_review():
    assert resolve_cj_category("unknown", "Unknown > Category").status == "REVIEW_REQUIRED"
    assert resolve_cj_category("", "").mapping_version == "v1"


def test_reviewed_product_override_resolves_contradictory_cj_category():
    result = resolve_cj_category("87CF251F-8D11-4DE0-A154-9694D9858EB3", "Home > Storage", "2503140216061603100")
    assert result.category_slug == "hair-style"
    assert result.status == "OVERRIDE"
    assert result.source == "ADMIN_PRODUCT_OVERRIDE"


def test_brand_rules_require_review_for_missing_or_new_brand():
    assert resolve_brand(explicit_brand="Generic").status == "GENERIC"
    assert resolve_brand(explicit_brand="New Brand").status == "BRAND_REVIEW_REQUIRED"
    assert resolve_brand(explicit_brand=None, manufacturer=None).status == "BRAND_REVIEW_REQUIRED"


def test_image_policy_accepts_only_approved_cj_hosts():
    assert is_allowed_image_url("https://cf.cjdropshipping.com/quick/product/image.jpg")
    assert is_allowed_image_url("https://oss-cf.cjdropshipping.com/product/image.jpg")
    assert not is_allowed_image_url("https://example.com/image.jpg")
    assert not is_allowed_image_url("http://cf.cjdropshipping.com/image.jpg")


def test_inventory_staleness_uses_utc_and_30_minute_window():
    now = datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)
    assert not is_inventory_stale(now - timedelta(minutes=29), now=now)
    assert is_inventory_stale(now - timedelta(minutes=31), now=now)
    assert is_inventory_stale(None, now=now)


def test_catalog_pricing_policy_requires_explicit_tax_treatment():
    policy = CatalogPricingPolicy(Decimal("98"), Decimal("2.36"), Decimal("4"), Decimal("20"))
    with pytest.raises(ValueError, match="Tax treatment"):
        policy.validate()


def test_catalog_pricing_policy_rejects_invalid_percentage_denominator():
    policy = CatalogPricingPolicy(Decimal("98"), Decimal("60"), Decimal("40"), Decimal("1"), "EXCLUSIVE", Decimal("0"))
    with pytest.raises(ValueError, match="less than 100"):
        policy.validate()
