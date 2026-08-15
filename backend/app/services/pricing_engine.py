from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from app.services.launch_pricing_policy import LaunchPricingPolicy


INR_QUANTUM = Decimal("0.01")
PERCENT_BASE = Decimal("100")


def round_inr(value: Decimal) -> Decimal:
    return value.quantize(INR_QUANTUM, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class PriceCalculation:
    supplier_cost_usd: Decimal
    shipping_cost_usd: Decimal
    usd_to_inr_exchange_rate: Decimal
    base_cost_inr: Decimal
    platform_fee_percent: Decimal
    platform_fee_inr: Decimal
    payment_fee_percent: Decimal
    payment_fee_inr: Decimal
    rto_reserve_percent: Decimal
    rto_reserve_inr: Decimal
    target_margin_percent: Decimal
    target_margin_inr: Decimal
    selling_price_inr: Decimal
    expected_profit_inr: Decimal


@dataclass(frozen=True)
class LaunchVariantPriceCalculation:
    supplier_cost_usd: Decimal
    pricing_fx_rate: Decimal
    shipping_cost_inr: Decimal
    landed_cost_inr: Decimal
    total_percentage_deduction: Decimal
    denominator: Decimal
    selling_price_inr: Decimal
    payment_gateway_pct: Decimal
    payment_fee_inr: Decimal
    rto_reserve_pct: Decimal
    rto_reserve_inr: Decimal
    contribution_before_cac_inr: Decimal
    target_contribution_margin_pct: Decimal
    target_contribution_inr: Decimal
    max_cac_for_target_margin_inr: Decimal
    target_cac_inr: Decimal
    contribution_after_target_cac_inr: Decimal
    target_margin_met: bool
    target_margin_status: str
    cac_target_supported: bool
    cac_target_status: str
    profitable_after_target_cac: bool
    unprofitable_after_target_cac: bool


def calculate_launch_variant_price(
    *,
    supplier_cost_usd: Decimal,
    shipping_cost_inr: Decimal,
    policy: LaunchPricingPolicy,
) -> LaunchVariantPriceCalculation:
    if supplier_cost_usd < 0:
        raise ValueError("Source USD supplier cost must be nonnegative")
    if shipping_cost_inr < 0:
        raise ValueError("Shipping cost must be nonnegative")

    landed_cost_inr = round_inr(supplier_cost_usd * policy.pricing_fx_rate + shipping_cost_inr)
    selling_price_inr = round_inr(landed_cost_inr / policy.denominator)
    payment_fee_inr = round_inr(
        selling_price_inr * policy.payment_gateway_pct / PERCENT_BASE
    )
    rto_reserve_inr = round_inr(
        selling_price_inr * policy.rto_reserve_pct / PERCENT_BASE
    )
    contribution_before_cac_inr = round_inr(
        selling_price_inr - landed_cost_inr - payment_fee_inr - rto_reserve_inr
    )
    target_contribution_inr = round_inr(
        selling_price_inr * policy.target_contribution_margin_pct / PERCENT_BASE
    )
    max_cac_for_target_margin_inr = round_inr(
        contribution_before_cac_inr - target_contribution_inr
    )
    contribution_after_target_cac_inr = round_inr(
        contribution_before_cac_inr - policy.target_cac_inr
    )
    rounding_tolerance = INR_QUANTUM
    target_margin_met = contribution_before_cac_inr + rounding_tolerance >= target_contribution_inr
    cac_target_supported = max_cac_for_target_margin_inr + rounding_tolerance >= policy.target_cac_inr
    profitable_after_target_cac = contribution_after_target_cac_inr >= 0

    return LaunchVariantPriceCalculation(
        supplier_cost_usd=supplier_cost_usd,
        pricing_fx_rate=policy.pricing_fx_rate,
        shipping_cost_inr=shipping_cost_inr,
        landed_cost_inr=landed_cost_inr,
        total_percentage_deduction=policy.total_percentage_deduction,
        denominator=policy.denominator,
        selling_price_inr=selling_price_inr,
        payment_gateway_pct=policy.payment_gateway_pct,
        payment_fee_inr=payment_fee_inr,
        rto_reserve_pct=policy.rto_reserve_pct,
        rto_reserve_inr=rto_reserve_inr,
        contribution_before_cac_inr=contribution_before_cac_inr,
        target_contribution_margin_pct=policy.target_contribution_margin_pct,
        target_contribution_inr=target_contribution_inr,
        max_cac_for_target_margin_inr=max_cac_for_target_margin_inr,
        target_cac_inr=policy.target_cac_inr,
        contribution_after_target_cac_inr=contribution_after_target_cac_inr,
        target_margin_met=target_margin_met,
        target_margin_status="TARGET_MARGIN_MET" if target_margin_met else "TARGET_MARGIN_NOT_MET",
        cac_target_supported=cac_target_supported,
        cac_target_status="CAC_TARGET_SUPPORTED" if cac_target_supported else "CAC_TARGET_NOT_SUPPORTED",
        profitable_after_target_cac=profitable_after_target_cac,
        unprofitable_after_target_cac=not profitable_after_target_cac,
    )


def calculate_margin_price(
    *,
    supplier_cost_usd: Decimal,
    shipping_cost_usd: Decimal,
    usd_to_inr_exchange_rate: Decimal,
    platform_fee_percent: Decimal,
    payment_fee_percent: Decimal,
    rto_reserve_percent: Decimal,
    target_margin_percent: Decimal,
) -> PriceCalculation:
    """Solve the margin equation, then round each INR output to paise using ROUND_HALF_UP."""
    total_percent = (
        platform_fee_percent
        + payment_fee_percent
        + rto_reserve_percent
        + target_margin_percent
    )
    denominator = Decimal("1") - (total_percent / PERCENT_BASE)
    if denominator <= 0:
        raise ValueError("Combined fee, reserve, and target margin percentages must be less than 100")

    converted_base_cost_inr = (
        supplier_cost_usd + shipping_cost_usd
    ) * usd_to_inr_exchange_rate
    base_cost_inr = round_inr(converted_base_cost_inr)
    selling_price_inr = round_inr(converted_base_cost_inr / denominator)
    platform_fee_inr = round_inr(selling_price_inr * platform_fee_percent / PERCENT_BASE)
    payment_fee_inr = round_inr(selling_price_inr * payment_fee_percent / PERCENT_BASE)
    rto_reserve_inr = round_inr(selling_price_inr * rto_reserve_percent / PERCENT_BASE)
    target_margin_inr = round_inr(selling_price_inr * target_margin_percent / PERCENT_BASE)
    expected_profit_inr = round_inr(
        selling_price_inr
        - base_cost_inr
        - platform_fee_inr
        - payment_fee_inr
        - rto_reserve_inr
    )

    return PriceCalculation(
        supplier_cost_usd=supplier_cost_usd,
        shipping_cost_usd=shipping_cost_usd,
        usd_to_inr_exchange_rate=usd_to_inr_exchange_rate,
        base_cost_inr=base_cost_inr,
        platform_fee_percent=platform_fee_percent,
        platform_fee_inr=platform_fee_inr,
        payment_fee_percent=payment_fee_percent,
        payment_fee_inr=payment_fee_inr,
        rto_reserve_percent=rto_reserve_percent,
        rto_reserve_inr=rto_reserve_inr,
        target_margin_percent=target_margin_percent,
        target_margin_inr=target_margin_inr,
        selling_price_inr=selling_price_inr,
        expected_profit_inr=expected_profit_inr,
    )