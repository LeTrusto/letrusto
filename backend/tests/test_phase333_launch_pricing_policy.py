from decimal import Decimal

import pytest

from app.core.config import Settings
from app.services.launch_pricing_policy import LaunchPricingPolicy, load_launch_pricing_policy
from app.services.pricing_engine import calculate_launch_variant_price


def test_approved_policy_constants_and_formula_outputs_are_exact_and_deterministic():
    policy = load_launch_pricing_policy(Settings(_env_file=None))

    assert policy.pricing_fx_rate == Decimal("98.00")
    assert policy.payment_gateway_pct == Decimal("2.36")
    assert policy.rto_reserve_pct == Decimal("4.00")
    assert policy.target_contribution_margin_pct == Decimal("20.00")
    assert policy.target_cac_inr == Decimal("150.00")
    assert policy.total_percentage_deduction == Decimal("0.2636")
    assert policy.denominator == Decimal("0.7364")

    results = [
        calculate_launch_variant_price(
            supplier_cost_usd=cost,
            shipping_cost_inr=Decimal("242.15"),
            policy=policy,
        )
        for cost in (Decimal("0.70"), Decimal("1.09"), Decimal("1.79"))
    ]
    repeated = calculate_launch_variant_price(
        supplier_cost_usd=Decimal("0.70"),
        shipping_cost_inr=Decimal("242.15"),
        policy=policy,
    )

    assert [result.landed_cost_inr for result in results] == [
        Decimal("310.75"), Decimal("348.97"), Decimal("417.57")
    ]
    assert [result.selling_price_inr for result in results] == [
        Decimal("421.99"), Decimal("473.89"), Decimal("567.04")
    ]
    assert [result.max_cac_for_target_margin_inr for result in results] == [
        Decimal("0.00"), Decimal("0.00"), Decimal("0.00")
    ]
    assert [result.target_cac_inr for result in results] == [
        Decimal("150.00"), Decimal("150.00"), Decimal("150.00")
    ]
    assert [result.contribution_after_target_cac_inr for result in results] == [
        Decimal("-65.60"), Decimal("-55.22"), Decimal("-36.59")
    ]
    assert repeated == results[0]
    assert len({result.selling_price_inr for result in results}) == 3
    assert all(result.target_margin_met for result in results)
    assert all(not result.cac_target_supported for result in results)
    assert all(result.unprofitable_after_target_cac for result in results)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("pricing_fx_rate", Decimal("0")),
        ("payment_gateway_pct", Decimal("-1")),
        ("rto_reserve_pct", Decimal("100")),
        ("target_contribution_margin_pct", Decimal("100")),
        ("target_cac_inr", Decimal("-0.01")),
    ],
)
def test_invalid_launch_policy_is_rejected(field: str, value: Decimal):
    values = {
        "pricing_fx_rate": Decimal("98.00"),
        "payment_gateway_pct": Decimal("2.36"),
        "rto_reserve_pct": Decimal("4.00"),
        "target_contribution_margin_pct": Decimal("20.00"),
        "target_cac_inr": Decimal("150.00"),
    }
    values[field] = value

    with pytest.raises(ValueError):
        LaunchPricingPolicy(**values)