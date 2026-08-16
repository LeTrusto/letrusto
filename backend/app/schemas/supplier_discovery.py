from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class DiscoveryShippingOption(BaseModel):
    carrier: str
    method: str
    cost_usd: float
    cost_inr: Decimal
    estimated_days: str
    trackable: bool


class DiscoveryVariantPricing(BaseModel):
    selling_price_inr: Decimal
    landed_cost_inr: Decimal
    contribution_before_cac_inr: Decimal
    contribution_after_target_cac_inr: Decimal
    max_cac_for_target_margin_inr: Decimal
    target_margin_met: bool
    cac_target_supported: bool


class DiscoveryVariant(BaseModel):
    supplier_variant_id: str
    supplier_variant_sku: str
    name: str
    option_key: str
    image: str
    cost_usd: float | None
    phase2_cost_inr: float | None
    launch_cost_inr: Decimal | None
    weight_grams: float | None
    total_inventory: int | None
    cj_inventory: int | None
    factory_inventory: int | None
    inventory_verification: str | None
    pricing: DiscoveryVariantPricing | None


class DiscoveryScoreBreakdown(BaseModel):
    supplier_reliability: int
    shipping_feasibility: int
    margin_score: int
    inventory_score: int
    data_completeness: int
    return_risk: int


class DiscoveryPhase2Economics(BaseModel):
    selling_price_inr: float | None
    contribution_inr: float | None
    contribution_pct: float | None
    margin_status: str
    unknown_costs: list[str]


class DiscoveryCommercialReview(BaseModel):
    decision: str
    reasons: list[str]
    blocking_reasons: list[str]
    cac_target_supported: bool
    target_margin_met_count: int
    target_margin_not_met_count: int
    valid_variant_count: int
    missing_variant_count: int


class DiscoveryRankingFactors(BaseModel):
    all_priced_variants_positive_before_cac: bool
    all_priced_variants_support_cac: bool
    cac_supported_variant_count: int
    priced_variant_count: int
    min_contribution_before_cac_inr: Decimal | None
    max_contribution_before_cac_inr: Decimal | None
    min_contribution_after_cac_inr: Decimal | None
    max_contribution_after_cac_inr: Decimal | None
    supplier_score: int
    cj_inventory: int | None
    data_completeness_score: int
    market_evidence_score: int = 0


class DiscoveryProduct(BaseModel):
    rank: int = 0
    processing_status: str = "SUCCESS"
    recommendation: str
    recommendation_reasons: list[str]
    canonical_product_id: str
    supplier: str
    supplier_sku: str
    title: str
    description: str
    category: str
    images: list[str]
    weight_grams: float | None
    total_inventory: int | None
    cj_inventory: int | None
    factory_inventory: int | None
    inventory_verification: str | None
    missing_fields: list[str]
    variants: list[DiscoveryVariant]
    shipping_based_on_variant_id: str | None
    shipping_applied_to_all_variants: bool = True
    shipping_can_ship: bool | None
    shipping_validation: str | None
    shipping_options: list[DiscoveryShippingOption]
    phase2_score: int
    phase2_verdict: str
    phase2_score_breakdown: DiscoveryScoreBreakdown
    phase2_score_notes: list[str]
    phase2_economics: DiscoveryPhase2Economics
    commercial_review: DiscoveryCommercialReview
    market_status: str = "INSUFFICIENT_MARKET_DATA"
    market_status_reason: str = "Discovery is non-persisting; no market evidence is loaded or created"
    ranking_factors: DiscoveryRankingFactors


class DiscoveryFailure(BaseModel):
    requested_product_id: str
    supplier_sku: str
    title: str
    stage: str
    recommendation: str = "REVIEW"
    error: str


class DiscoveryVerdictCounts(BaseModel):
    approved_candidate: int = 0
    review: int = 0
    rejected: int = 0


class SupplierDiscoveryResponse(BaseModel):
    query: str
    destination: str
    elapsed_seconds: float
    requested_count: int
    returned_count: int
    success_count: int
    failed_count: int
    verdict_counts: DiscoveryVerdictCounts
    ranking_method: list[str] = Field(default_factory=lambda: [
        "all priced variants have positive contribution before CAC",
        "all priced variants support target CAC",
        "CAC-supported variant count",
        "Phase 2 supplier score",
        "CJ sellable inventory",
        "Phase 2 data completeness score",
        "market evidence score",
        "canonical product ID ascending tie-break",
    ])
    top_recommendations: list[DiscoveryProduct]
    products: list[DiscoveryProduct]
    failures: list[DiscoveryFailure]