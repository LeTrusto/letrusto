from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from app.services.launch_pricing_policy import LaunchPricingPolicy
from app.services.pricing_engine import PERCENT_BASE, calculate_launch_variant_price, round_inr


@dataclass(frozen=True)
class CommercialReviewResult:
    decision: str
    reasons: list[str]
    blocking_reasons: list[str]
    target_margin_percent: Decimal
    target_margin_met_count: int
    target_margin_not_met_count: int
    target_cac_inr: Decimal
    cac_target_supported: bool
    cac_target_status: str
    cj_inventory: int | None
    market_price_status: str
    active_variant_count: int
    valid_variant_count: int
    missing_variant_count: int
    price_discrepancy_count: int
    supplier_validation_status: str | None
    supplier_validation_score: int | None
    supplier_validation_issues: list[str]


def evaluate_commercial_product(product: Any, policy: LaunchPricingPolicy) -> CommercialReviewResult:
    blocking_reasons: list[str] = []
    informational_reasons: list[str] = []
    active_variants = [variant for variant in product.variants if variant.active]
    valid_variant_count = 0
    missing_variant_count = 0
    price_discrepancy_count = 0
    target_margin_met_count = 0
    target_margin_not_met_count = 0
    cac_supported = bool(active_variants)

    completeness_values = (
        product.name,
        product.description,
        product.supplier,
        product.supplier_product_id,
    )
    variants_complete = bool(active_variants) and all(
        variant.supplier_variant_id and variant.supplier_variant_sku
        for variant in active_variants
    )
    images_complete = any(getattr(image, "url", "") for image in product.images)
    if not all(value and str(value).strip() for value in completeness_values) or not images_complete or not variants_complete:
        blocking_reasons.append("INCOMPLETE_PRODUCT_DATA")

    shipping_valid = product.shipping_cost is not None and product.shipping_cost >= 0
    if product.shipping_cost is None:
        blocking_reasons.append("SHIPPING_COST_MISSING")
    elif product.shipping_cost < 0:
        blocking_reasons.append("SHIPPING_COST_INVALID")

    for variant in active_variants:
        if variant.supplier_cost_usd is None or variant.supplier_cost_usd < 0:
            missing_variant_count += 1
            cac_supported = False
            continue
        if variant.selling_price is None or variant.selling_price < 0:
            missing_variant_count += 1
            cac_supported = False
            continue
        if not shipping_valid:
            missing_variant_count += 1
            cac_supported = False
            continue

        calculation = calculate_launch_variant_price(
            supplier_cost_usd=variant.supplier_cost_usd,
            shipping_cost_inr=product.shipping_cost,
            policy=policy,
        )
        valid_variant_count += 1
        if variant.selling_price != calculation.selling_price_inr:
            price_discrepancy_count += 1
        payment_fee = round_inr(variant.selling_price * policy.payment_gateway_pct / PERCENT_BASE)
        rto_reserve = round_inr(variant.selling_price * policy.rto_reserve_pct / PERCENT_BASE)
        contribution = round_inr(
            variant.selling_price - calculation.landed_cost_inr - payment_fee - rto_reserve
        )
        target_contribution = round_inr(
            variant.selling_price * policy.target_contribution_margin_pct / PERCENT_BASE
        )
        max_cac = round_inr(contribution - target_contribution)
        if contribution + Decimal("0.01") >= target_contribution:
            target_margin_met_count += 1
        else:
            target_margin_not_met_count += 1
        if max_cac + Decimal("0.01") < policy.target_cac_inr:
            cac_supported = False

    if any(
        variant.supplier_cost_usd is None or variant.supplier_cost_usd < 0
        for variant in active_variants
    ):
        blocking_reasons.append("SUPPLIER_COST_MISSING")
    if not active_variants or missing_variant_count:
        blocking_reasons.append("VARIANT_PRICE_MISSING")
    if price_discrepancy_count:
        blocking_reasons.append("VARIANT_PRICE_DISCREPANCY")
    if target_margin_not_met_count:
        blocking_reasons.append("TARGET_MARGIN_NOT_MET")

    if product.cj_inventory is None or product.cj_inventory <= 0:
        blocking_reasons.append("NO_SELLABLE_INVENTORY")

    supplier_validation_status = getattr(product, "supplier_validation_status", None)
    explicit_rejection = supplier_validation_status == "REJECT"
    if supplier_validation_status is None:
        blocking_reasons.append("VALIDATION_NOT_AVAILABLE")
    elif supplier_validation_status == "REVIEW":
        blocking_reasons.append("SUPPLIER_VALIDATION_REVIEW")
    elif explicit_rejection:
        blocking_reasons.append("SUPPLIER_VALIDATION_REJECTED")

    if not cac_supported:
        informational_reasons.append("CAC_TARGET_NOT_SUPPORTED")

    blocking_reasons = list(dict.fromkeys(blocking_reasons))
    decision = "REJECTED" if explicit_rejection else "APPROVED" if not blocking_reasons else "REVIEW"
    return CommercialReviewResult(
        decision=decision,
        reasons=blocking_reasons + informational_reasons,
        blocking_reasons=blocking_reasons,
        target_margin_percent=policy.target_contribution_margin_pct,
        target_margin_met_count=target_margin_met_count,
        target_margin_not_met_count=target_margin_not_met_count,
        target_cac_inr=policy.target_cac_inr,
        cac_target_supported=cac_supported,
        cac_target_status="CAC_TARGET_SUPPORTED" if cac_supported else "CAC_TARGET_NOT_SUPPORTED",
        cj_inventory=product.cj_inventory,
        market_price_status="NOT_EVALUATED",
        active_variant_count=len(active_variants),
        valid_variant_count=valid_variant_count,
        missing_variant_count=missing_variant_count,
        price_discrepancy_count=price_discrepancy_count,
        supplier_validation_status=supplier_validation_status,
        supplier_validation_score=getattr(product, "supplier_validation_score", None),
        supplier_validation_issues=getattr(product, "supplier_validation_notes", None) or [],
    )