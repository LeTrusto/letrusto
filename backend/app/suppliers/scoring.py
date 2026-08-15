"""Product quality score for supplier validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.suppliers.base import ShippingResult, ShippingValidation
from app.suppliers.economics import MarginStatus, ProductEconomics
from app.suppliers.normalizer import NormalizedProduct


class ScoreVerdict(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    REJECT = "REJECT"


@dataclass
class ScoreBreakdown:
    supplier_reliability: int  # 0-15
    shipping_feasibility: int  # 0-25
    margin_score: int  # 0-25
    inventory_score: int  # 0-15
    data_completeness: int  # 0-10
    return_risk: int  # 0-10

    @property
    def total(self) -> int:
        return (
            self.supplier_reliability
            + self.shipping_feasibility
            + self.margin_score
            + self.inventory_score
            + self.data_completeness
            + self.return_risk
        )


@dataclass
class ProductScore:
    product_id: str
    score: int
    verdict: ScoreVerdict
    breakdown: ScoreBreakdown
    notes: list[str]


@dataclass
class ScoreThresholds:
    pass_threshold: int = 65
    review_threshold: int = 40


def score_product(
    product: NormalizedProduct,
    economics: ProductEconomics | None = None,
    shipping: ShippingResult | None = None,
    *,
    thresholds: ScoreThresholds | None = None,
) -> ProductScore:
    cfg = thresholds or ScoreThresholds()
    notes: list[str] = []

    # 1. Supplier reliability (0-15)
    reliability = 10  # baseline for CJ (established platform)
    if product.total_inventory is not None and product.total_inventory > 100:
        reliability += 5
    elif product.total_inventory is not None and product.total_inventory > 0:
        reliability += 2
    else:
        notes.append("Low or unknown inventory")

    # 2. Shipping feasibility (0-25)
    ship_score = 0
    if shipping is not None:
        if shipping.validation == ShippingValidation.VERIFIED and shipping.can_ship:
            ship_score = 20
            cheapest = shipping.options[0] if shipping.options else None
            if cheapest and cheapest.cost_usd < 5:
                ship_score = 25
            elif cheapest and cheapest.cost_usd > 15:
                ship_score = 12
                notes.append(f"High shipping cost: ${cheapest.cost_usd:.2f}")
        elif shipping.validation == ShippingValidation.REQUIRES_MANUAL_VALIDATION:
            ship_score = 5
            notes.append("Shipping requires manual validation")
        else:
            notes.append("Cannot ship to destination")
    else:
        ship_score = 0
        notes.append("Shipping not validated")

    # 3. Margin (0-25)
    margin = 0
    if economics is not None:
        if economics.margin_status == MarginStatus.PROFITABLE:
            margin = 25
        elif economics.margin_status == MarginStatus.MARGINAL:
            margin = 15
            notes.append("Thin margins")
        elif economics.margin_status == MarginStatus.UNPROFITABLE:
            margin = 0
            notes.append("Unprofitable at target markup")
        else:
            margin = 5
            notes.append("Margin unknown — missing cost inputs")
    else:
        notes.append("Economics not calculated")

    # 4. Inventory (0-15)
    inv_score = 0
    if product.total_inventory is not None:
        if product.total_inventory >= 500:
            inv_score = 15
        elif product.total_inventory >= 100:
            inv_score = 10
        elif product.total_inventory >= 10:
            inv_score = 5
        else:
            notes.append("Very low inventory")
    else:
        notes.append("Inventory unknown")

    # 5. Data completeness (0-10)
    completeness = 10 - len(product.missing_fields) * 2
    completeness = max(completeness, 0)
    if product.missing_fields:
        notes.append(f"Missing: {', '.join(product.missing_fields)}")

    # 6. Return risk (0-10) — lower risk = higher score
    return_risk = 8  # baseline for accessories/jewellery (low-risk)
    if product.weight_grams is not None and product.weight_grams > 2000:
        return_risk = 4
        notes.append("Heavy product — higher shipping/return cost")
    if any(p in ("LIQUID", "BATTERY", "POWDER", "SPECIAL") for p in product.logistics_properties):
        return_risk = 2
        notes.append("Restricted logistics properties")

    breakdown = ScoreBreakdown(
        supplier_reliability=reliability,
        shipping_feasibility=ship_score,
        margin_score=margin,
        inventory_score=inv_score,
        data_completeness=completeness,
        return_risk=return_risk,
    )

    total = breakdown.total
    if total >= cfg.pass_threshold:
        verdict = ScoreVerdict.PASS
    elif total >= cfg.review_threshold:
        verdict = ScoreVerdict.REVIEW
    else:
        verdict = ScoreVerdict.REJECT

    return ProductScore(
        product_id=product.letrusto_product_id,
        score=total,
        verdict=verdict,
        breakdown=breakdown,
        notes=notes,
    )
