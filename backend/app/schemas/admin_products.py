from decimal import Decimal
from typing import Literal
from uuid import UUID

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, field_validator


CatalogStatus = Literal["DRAFT", "ACTIVE", "PAUSED"]
CommercialStatus = Literal["DRAFT", "REVIEW", "APPROVED", "REJECTED"]
SupplierValidationStatus = Literal["PASS", "REVIEW", "REJECT"]
MarketEvidenceStatus = Literal[
    "INSUFFICIENT_MARKET_DATA", "MARKET_COMPETITIVE", "MARKET_ABOVE_OBSERVED"
]


class MarketEvidenceCreate(BaseModel):
    competitor_name: str = Field(min_length=1, max_length=160)
    product_name: str = Field(min_length=1, max_length=240)
    source_url: HttpUrl
    observed_price_inr: Decimal = Field(gt=0, allow_inf_nan=False, max_digits=12, decimal_places=2)
    currency: Literal["INR"] = "INR"
    variant_description: str | None = Field(default=None, max_length=240)
    notes: str | None = None
    checked_at: datetime | None = None

    @field_validator("competitor_name", "product_name")
    @classmethod
    def required_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value.strip()


class MarketEvidenceDTO(BaseModel):
    id: UUID
    product_id: UUID
    competitor_name: str
    product_name: str
    source_url: str
    observed_price_inr: Decimal
    currency: Literal["INR"]
    variant_description: str | None
    notes: str | None
    checked_at: datetime
    created_at: datetime
    updated_at: datetime


class MarketEvidenceAnalysis(BaseModel):
    observation_count: int
    minimum_price_inr: Decimal | None
    maximum_price_inr: Decimal | None
    average_price_inr: Decimal | None
    median_price_inr: Decimal | None
    status: MarketEvidenceStatus
    evaluated_variant_count: int
    letrusto_variant_min_price_inr: Decimal | None
    letrusto_variant_max_price_inr: Decimal | None
    stored_product_selling_price_inr: Decimal | None


class MarketEvidenceResponse(BaseModel):
    product_id: UUID
    evidence: list[MarketEvidenceDTO]
    analysis: MarketEvidenceAnalysis


class ProductImportRequest(BaseModel):
    supplier: Literal["cj"]
    supplier_product_id: str
    destination: str = "IN"


class ProductStatusUpdate(BaseModel):
    status: CatalogStatus


class ProductRejectionRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class PriceCalculationRequest(BaseModel):
    supplier_cost_usd: Decimal = Field(ge=0, allow_inf_nan=False)
    shipping_cost_usd: Decimal = Field(ge=0, allow_inf_nan=False)
    usd_to_inr_exchange_rate: Decimal = Field(gt=0, allow_inf_nan=False)
    platform_fee_percent: Decimal = Field(ge=0, lt=100, allow_inf_nan=False)
    payment_fee_percent: Decimal = Field(ge=0, lt=100, allow_inf_nan=False)
    rto_reserve_percent: Decimal = Field(ge=0, lt=100, allow_inf_nan=False)
    target_margin_percent: Decimal = Field(ge=0, lt=100, allow_inf_nan=False)


class PriceCalculationResponse(BaseModel):
    product_id: UUID
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
    currency: Literal["INR"] = "INR"
    rounding_rule: Literal["ROUND_HALF_UP_TO_0.01_INR"] = "ROUND_HALF_UP_TO_0.01_INR"


class VariantPriceCalculation(BaseModel):
    variant_id: UUID
    supplier_variant_id: str
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
    target_margin_status: Literal["TARGET_MARGIN_MET", "TARGET_MARGIN_NOT_MET"]
    cac_target_supported: bool
    cac_target_status: Literal["CAC_TARGET_SUPPORTED", "CAC_TARGET_NOT_SUPPORTED"]
    profitable_after_target_cac: bool
    unprofitable_after_target_cac: bool


class VariantPriceCalculationResponse(BaseModel):
    product_id: UUID
    variants: list[VariantPriceCalculation]
    currency: Literal["INR"] = "INR"
    rounding_rule: Literal["ROUND_HALF_UP_TO_0.01_INR"] = "ROUND_HALF_UP_TO_0.01_INR"


class CommercialReviewResponse(BaseModel):
    product_id: UUID
    decision: CommercialStatus
    reasons: list[str]
    blocking_reasons: list[str]
    reviewed_at: str
    target_margin_percent: Decimal
    target_margin_met_count: int
    target_margin_not_met_count: int
    target_cac_inr: Decimal
    cac_target_supported: bool
    cac_target_status: Literal["CAC_TARGET_SUPPORTED", "CAC_TARGET_NOT_SUPPORTED"]
    cj_inventory: int | None
    market_price_status: Literal["NOT_EVALUATED"]
    active_variant_count: int
    valid_variant_count: int
    missing_variant_count: int
    price_discrepancy_count: int
    supplier_validation_status: SupplierValidationStatus | None
    supplier_validation_score: int | None
    supplier_validation_issues: list[str]


class AdminProductVariantDTO(BaseModel):
    id: UUID
    supplier_variant_id: str
    supplier_variant_sku: str
    name: str
    attributes: str
    supplier_cost: Decimal | None
    supplier_cost_usd: Decimal | None
    selling_price: Decimal | None
    total_inventory: int | None
    cj_inventory: int | None
    factory_inventory: int | None
    verified_warehouse: str | None
    weight_grams: Decimal | None
    active: bool
    position: int


class AdminProductDTO(BaseModel):
    id: UUID
    slug: str
    name: str
    description: str
    status: str
    supplier: str | None
    supplier_product_id: str | None
    supplier_source_url: str | None
    supplier_cost: Decimal | None
    shipping_cost: Decimal | None
    selling_price: Decimal | None
    currency: str
    total_inventory: int | None
    cj_inventory: int | None
    factory_inventory: int | None
    verified_warehouse: str | None
    last_supplier_sync_at: str | None
    commercial_status: CommercialStatus
    commercial_reasons: list[str]
    commercial_reviewed_at: str | None
    commercial_target_margin_percent: Decimal
    commercial_target_cac_inr: Decimal
    commercial_cac_supported: bool | None
    supplier_validation_status: SupplierValidationStatus | None
    supplier_validation_score: int | None
    supplier_validation_notes: list[str]
    supplier_validation_details: dict | None
    supplier_validated_at: str | None
    approval_decided_at: str | None
    approval_decided_by_user_id: UUID | None
    approval_rejection_reason: str | None
    approval_evidence: dict | None
    market_price_status: Literal["NOT_EVALUATED"] = "NOT_EVALUATED"
    images: list[str]
    variants: list[AdminProductVariantDTO]


class AdminProductListResponse(BaseModel):
    products: list[AdminProductDTO]
    total: int
