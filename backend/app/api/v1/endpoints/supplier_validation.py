"""Supplier validation API — development-only endpoints for Phase 2."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.api.deps import get_current_admin
from app.models.entities import User
from app.suppliers.base import ShippingValidation
from app.suppliers.economics import EconomicsConfig, calculate_economics
from app.suppliers.factory import build_supplier_adapter
from app.suppliers.normalizer import normalize_product
from app.suppliers.scoring import score_product

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/supplier-validation", tags=["supplier-validation"])


class ValidationProductDTO(BaseModel):
    product_id: str
    supplier: str
    supplier_sku: str
    title: str
    category: str
    cost_usd: float | None
    cost_inr: float | None
    images: int
    variants: int
    inventory: int | None
    warehouse: str
    weight_grams: float | None
    missing_fields: list[str]
    shipping_can_ship: bool | None = None
    shipping_validation: str | None = None
    shipping_cheapest_usd: float | None = None
    shipping_estimated_days: str | None = None
    shipping_carrier: str | None = None
    selling_price_inr: float | None = None
    contribution_inr: float | None = None
    contribution_pct: float | None = None
    margin_status: str | None = None
    unknown_costs: list[str] = []
    score: int | None = None
    verdict: str | None = None
    score_notes: list[str] = []


class ValidationSummaryDTO(BaseModel):
    supplier: str
    products_imported: int
    products_passing: int
    products_review: int
    products_rejected: int
    avg_supplier_cost_usd: float | None
    avg_contribution_inr: float | None
    missing_data_fields: dict[str, int]
    shipping_validation_status: str
    products: list[ValidationProductDTO]


@router.get("/search", response_model=ValidationSummaryDTO)
async def validate_supplier_products(
    keyword: str = Query(..., min_length=1, description="Search keyword for supplier products"),
    destination: str = Query("IN", description="Destination country code"),
    page_size: int = Query(20, ge=1, le=50),
    _: User = Depends(get_current_admin),
) -> Any:
    adapter = build_supplier_adapter()

    if not await adapter.authenticate():
        return _empty_summary(adapter.supplier_name, "Authentication failed")

    raw_products = await adapter.search_products(keyword, page_size=page_size)
    if not raw_products:
        return _empty_summary(adapter.supplier_name, "No products found")

    results: list[ValidationProductDTO] = []
    passing = 0
    review = 0
    rejected = 0
    costs_usd: list[float] = []
    contributions: list[float] = []
    missing_counts: dict[str, int] = {}

    config = EconomicsConfig()

    for raw in raw_products:
        # Get full product detail for variants
        detail = await adapter.get_product(raw.supplier_product_id)
        if detail:
            raw = detail

        normalized = normalize_product(raw, usd_to_inr=config.usd_to_inr)

        # Track missing fields
        for f in normalized.missing_fields:
            missing_counts[f] = missing_counts.get(f, 0) + 1

        # Shipping validation
        shipping = None
        first_variant_id = ""
        if normalized.variants:
            first_variant_id = normalized.variants[0].supplier_variant_id
        elif raw.supplier_product_id:
            first_variant_id = raw.supplier_product_id

        if first_variant_id:
            shipping = await adapter.calculate_shipping(
                first_variant_id, destination, origin_country=normalized.warehouse_country or "CN"
            )

        # Economics
        shipping_usd = None
        if shipping and shipping.options:
            shipping_usd = shipping.options[0].cost_usd

        economics = calculate_economics(normalized, shipping_cost_usd=shipping_usd, config=config)

        # Scoring
        product_score = score_product(normalized, economics=economics, shipping=shipping)

        if product_score.verdict.value == "PASS":
            passing += 1
        elif product_score.verdict.value == "REVIEW":
            review += 1
        else:
            rejected += 1

        if normalized.cost_usd is not None:
            costs_usd.append(normalized.cost_usd)
        if economics.contribution_inr is not None:
            contributions.append(economics.contribution_inr)

        dto = ValidationProductDTO(
            product_id=normalized.letrusto_product_id,
            supplier=normalized.supplier_id,
            supplier_sku=normalized.supplier_sku,
            title=normalized.title,
            category=normalized.category,
            cost_usd=normalized.cost_usd,
            cost_inr=normalized.cost_inr,
            images=len(normalized.images),
            variants=len(normalized.variants),
            inventory=normalized.total_inventory,
            warehouse=normalized.warehouse_country,
            weight_grams=normalized.weight_grams,
            missing_fields=normalized.missing_fields,
            shipping_can_ship=shipping.can_ship if shipping else None,
            shipping_validation=shipping.validation.value if shipping else None,
            shipping_cheapest_usd=shipping.options[0].cost_usd if shipping and shipping.options else None,
            shipping_estimated_days=shipping.options[0].estimated_days if shipping and shipping.options else None,
            shipping_carrier=shipping.options[0].carrier if shipping and shipping.options else None,
            selling_price_inr=economics.selling_price_inr,
            contribution_inr=economics.contribution_inr,
            contribution_pct=economics.contribution_pct,
            margin_status=economics.margin_status.value,
            unknown_costs=economics.unknown_costs,
            score=product_score.score,
            verdict=product_score.verdict.value,
            score_notes=product_score.notes,
        )
        results.append(dto)

    # Determine overall shipping status
    shipping_statuses = [r.shipping_validation for r in results if r.shipping_validation]
    if all(s == ShippingValidation.VERIFIED.value for s in shipping_statuses):
        overall_shipping = "ALL_VERIFIED"
    elif any(s == ShippingValidation.VERIFIED.value for s in shipping_statuses):
        overall_shipping = "PARTIAL"
    else:
        overall_shipping = "NOT_VALIDATED"

    return ValidationSummaryDTO(
        supplier=adapter.supplier_name,
        products_imported=len(results),
        products_passing=passing,
        products_review=review,
        products_rejected=rejected,
        avg_supplier_cost_usd=round(sum(costs_usd) / len(costs_usd), 2) if costs_usd else None,
        avg_contribution_inr=round(sum(contributions) / len(contributions), 2) if contributions else None,
        missing_data_fields=missing_counts,
        shipping_validation_status=overall_shipping,
        products=results,
    )


def _empty_summary(supplier: str, reason: str) -> ValidationSummaryDTO:
    return ValidationSummaryDTO(
        supplier=supplier,
        products_imported=0,
        products_passing=0,
        products_review=0,
        products_rejected=0,
        avg_supplier_cost_usd=None,
        avg_contribution_inr=None,
        missing_data_fields={},
        shipping_validation_status=reason,
        products=[],
    )
