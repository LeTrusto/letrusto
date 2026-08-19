from decimal import Decimal

import pytest

from app.core.catalog_readiness import CatalogPricingPolicy, UNREGISTERED_NO_GSTIN
from app.core.config import Settings
from app.services.catalog_readiness_service import CatalogReadinessService
from app.services.pricing_engine import calculate_launch_variant_price
from app.services.launch_pricing_policy import LaunchPricingPolicy


def test_unregistered_no_gstin_is_valid_without_tax_rate():
    policy = CatalogPricingPolicy(
        pricing_fx_rate=Decimal("98"),
        payment_fee_pct=Decimal("2.36"),
        rto_reserve_pct=Decimal("4"),
        target_margin_pct=Decimal("20"),
        tax_treatment=UNREGISTERED_NO_GSTIN,
        tax_rate_pct=None,
    )
    policy.validate()
    assert policy.tax_rate_pct is None


def test_unregistered_no_gstin_is_not_a_tax_exemption_or_rate():
    policy = CatalogPricingPolicy(
        pricing_fx_rate=Decimal("98"),
        payment_fee_pct=Decimal("2.36"),
        rto_reserve_pct=Decimal("4"),
        target_margin_pct=Decimal("20"),
        tax_treatment=UNREGISTERED_NO_GSTIN,
    )
    policy.validate()
    assert policy.tax_treatment == "UNREGISTERED_NO_GSTIN"
    assert policy.tax_rate_pct is None


def test_unregistered_no_gstin_rejects_accidental_tax_rate():
    policy = CatalogPricingPolicy(
        pricing_fx_rate=Decimal("98"),
        payment_fee_pct=Decimal("2.36"),
        rto_reserve_pct=Decimal("4"),
        target_margin_pct=Decimal("20"),
        tax_treatment=UNREGISTERED_NO_GSTIN,
        tax_rate_pct=Decimal("18"),
    )
    with pytest.raises(ValueError, match="must not configure a tax rate"):
        policy.validate()


def test_pricing_formula_remains_unchanged_without_gst_amount():
    policy = LaunchPricingPolicy(
        pricing_fx_rate=Decimal("98"),
        payment_gateway_pct=Decimal("2.36"),
        rto_reserve_pct=Decimal("4"),
        target_contribution_margin_pct=Decimal("20"),
        target_cac_inr=Decimal("150"),
    )
    result = calculate_launch_variant_price(
        supplier_cost_usd=Decimal("1"),
        shipping_cost_inr=Decimal("100"),
        policy=policy,
    )
    expected_landed = Decimal("198")
    expected_price = (expected_landed / policy.denominator).quantize(Decimal("0.01"))
    assert result.landed_cost_inr == expected_landed
    assert result.selling_price_inr == expected_price
    assert not hasattr(result, "gst_amount")
    assert not hasattr(result, "tax_amount")


def test_default_settings_use_no_gstin_state():
    settings = Settings()
    assert settings.CATALOG_TAX_TREATMENT == UNREGISTERED_NO_GSTIN
    assert settings.CATALOG_TAX_RATE_PCT is None
