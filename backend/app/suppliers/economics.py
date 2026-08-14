"""Product economics / contribution margin calculation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.suppliers.normalizer import NormalizedProduct


class CostStatus(str, Enum):
    KNOWN = "KNOWN"
    ESTIMATED = "ESTIMATED"
    UNKNOWN = "UNKNOWN"


class MarginStatus(str, Enum):
    PROFITABLE = "PROFITABLE"
    MARGINAL = "MARGINAL"
    UNPROFITABLE = "UNPROFITABLE"
    UNKNOWN = "UNKNOWN"


@dataclass
class CostLine:
    label: str
    amount_inr: float | None
    status: CostStatus


@dataclass
class ProductEconomics:
    product_id: str
    product_title: str
    supplier: str

    supplier_cost_inr: CostLine
    shipping_cost_inr: CostLine
    payment_fee_inr: CostLine
    rto_reserve_inr: CostLine
    creator_commission_inr: CostLine
    marketing_allowance_inr: CostLine

    total_variable_cost_inr: float | None
    selling_price_inr: float | None
    contribution_inr: float | None
    contribution_pct: float | None
    margin_status: MarginStatus
    unknown_costs: list[str]


@dataclass
class EconomicsConfig:
    """Configurable rates — do NOT invent values, mark as UNKNOWN if unavailable."""

    payment_fee_pct: float = 0.025  # ~2.5% Razorpay-class gateway
    rto_reserve_pct: float | None = None  # UNKNOWN until we have data
    creator_commission_pct: float = 0.10  # 10% creator commission
    marketing_allowance_pct: float = 0.05  # 5% blended marketing
    usd_to_inr: float = 83.5
    # Selling price multiplier over supplier cost (target markup)
    target_markup: float = 2.5


def calculate_economics(
    product: NormalizedProduct,
    *,
    shipping_cost_usd: float | None = None,
    config: EconomicsConfig | None = None,
) -> ProductEconomics:
    cfg = config or EconomicsConfig()
    unknowns: list[str] = []

    # Supplier cost
    supplier_cost_inr = product.cost_inr
    supplier_line = CostLine(
        "Supplier Cost",
        supplier_cost_inr,
        CostStatus.KNOWN if supplier_cost_inr is not None else CostStatus.UNKNOWN,
    )
    if supplier_cost_inr is None:
        unknowns.append("supplier_cost")

    # Shipping
    shipping_inr: float | None = None
    shipping_status = CostStatus.UNKNOWN
    if shipping_cost_usd is not None:
        shipping_inr = round(shipping_cost_usd * cfg.usd_to_inr, 2)
        shipping_status = CostStatus.KNOWN
    else:
        unknowns.append("shipping_cost")
    shipping_line = CostLine("Shipping to India", shipping_inr, shipping_status)

    # Selling price — derived from target markup if supplier cost known
    selling_price: float | None = None
    if supplier_cost_inr is not None:
        selling_price = round(supplier_cost_inr * cfg.target_markup)
        # Round to nearest ₹49/₹99 price point
        selling_price = _round_to_price_point(selling_price)

    # Payment fee
    payment_inr: float | None = None
    if selling_price is not None:
        payment_inr = round(selling_price * cfg.payment_fee_pct, 2)
    payment_line = CostLine(
        "Payment Fee", payment_inr, CostStatus.ESTIMATED if payment_inr else CostStatus.UNKNOWN
    )

    # RTO reserve
    rto_inr: float | None = None
    rto_status = CostStatus.UNKNOWN
    if cfg.rto_reserve_pct is not None and selling_price is not None:
        rto_inr = round(selling_price * cfg.rto_reserve_pct, 2)
        rto_status = CostStatus.ESTIMATED
    else:
        unknowns.append("rto_reserve")
    rto_line = CostLine("RTO/Return Reserve", rto_inr, rto_status)

    # Creator commission
    creator_inr: float | None = None
    if selling_price is not None:
        creator_inr = round(selling_price * cfg.creator_commission_pct, 2)
    creator_line = CostLine(
        "Creator Commission", creator_inr, CostStatus.ESTIMATED if creator_inr else CostStatus.UNKNOWN
    )

    # Marketing
    marketing_inr: float | None = None
    if selling_price is not None:
        marketing_inr = round(selling_price * cfg.marketing_allowance_pct, 2)
    marketing_line = CostLine(
        "Marketing Allowance", marketing_inr, CostStatus.ESTIMATED if marketing_inr else CostStatus.UNKNOWN
    )

    # Total variable cost
    cost_parts = [supplier_cost_inr, shipping_inr, payment_inr, rto_inr, creator_inr, marketing_inr]
    known_parts = [c for c in cost_parts if c is not None]
    total_variable: float | None = round(sum(known_parts), 2) if known_parts else None

    # Contribution
    contribution: float | None = None
    contribution_pct: float | None = None
    if selling_price is not None and total_variable is not None:
        contribution = round(selling_price - total_variable, 2)
        contribution_pct = round((contribution / selling_price) * 100, 1) if selling_price > 0 else 0.0

    # Margin status
    if unknowns:
        margin_status = MarginStatus.UNKNOWN
    elif contribution is not None:
        if contribution_pct is not None and contribution_pct >= 20:
            margin_status = MarginStatus.PROFITABLE
        elif contribution_pct is not None and contribution_pct >= 5:
            margin_status = MarginStatus.MARGINAL
        else:
            margin_status = MarginStatus.UNPROFITABLE
    else:
        margin_status = MarginStatus.UNKNOWN

    return ProductEconomics(
        product_id=product.letrusto_product_id,
        product_title=product.title,
        supplier=product.supplier_id,
        supplier_cost_inr=supplier_line,
        shipping_cost_inr=shipping_line,
        payment_fee_inr=payment_line,
        rto_reserve_inr=rto_line,
        creator_commission_inr=creator_line,
        marketing_allowance_inr=marketing_line,
        total_variable_cost_inr=total_variable,
        selling_price_inr=selling_price,
        contribution_inr=contribution,
        contribution_pct=contribution_pct,
        margin_status=margin_status,
        unknown_costs=unknowns,
    )


def _round_to_price_point(price: float) -> float:
    """Round to nearest ₹49/₹99 price point."""
    if price <= 99:
        return 99
    base = int(price // 100) * 100
    remainder = price - base
    if remainder <= 49:
        return base + 49
    return base + 99
