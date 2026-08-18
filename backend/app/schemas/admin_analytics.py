from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class MetricAvailability(BaseModel):
    value: Decimal | None
    status: str
    reason: str | None = None


class AnalyticsPeriod(BaseModel):
    label: str
    start: datetime
    end: datetime
    timezone: str = "UTC"
    order_count_date_basis: str = "created_at"
    sales_date_basis: str = "paid_at"
    refund_date_basis: str = "completed_at"


class AnalyticsSummary(BaseModel):
    period: AnalyticsPeriod
    gross_order_value: Decimal
    paid_sales: Decimal
    refunded_amount: Decimal
    net_sales: Decimal
    payment_fees: MetricAvailability
    landed_cost: MetricAvailability
    shipping_cost: MetricAvailability
    contribution_before_cac: MetricAvailability
    cac: MetricAvailability
    contribution_after_cac: MetricAvailability
    order_count: int
    paid_order_count: int
    refunded_order_count: int
    pending_payment_count: int
    average_order_value: Decimal | None
    status_breakdown: dict[str, int]
    policy_assumptions: dict[str, Decimal]
    contribution_status: str
    contribution_margin_percent: Decimal | None


class ProductPerformanceDTO(BaseModel):
    product_id: UUID | None
    product_name: str
    orders: int
    units_sold: int
    paid_units: int
    gross_sales: Decimal
    refunds: Decimal
    net_sales: Decimal
    landed_cost: MetricAvailability
    shipping_cost: MetricAvailability
    contribution_before_cac: MetricAvailability
    cac: MetricAvailability
    contribution_after_cac: MetricAvailability
    average_selling_price: Decimal | None
    inventory_available: int | None
    cj_inventory: int | None
    factory_inventory: int | None
    data_quality: list[str]
    contribution_status: str
    contribution_margin_percent: Decimal | None


class VariantPerformanceDTO(ProductPerformanceDTO):
    variant_id: UUID | None
    variant_name: str
    supplier_variant_id: str | None
    supplier_variant_sku: str | None


class InventoryAnalyticsDTO(BaseModel):
    product_id: UUID
    product_name: str
    variant_id: UUID
    variant_name: str
    cj_inventory: int | None
    factory_inventory: int | None
    active_reservations: int
    available_customer_inventory: int
    sellable_inventory_status: str


class SalesTrendPoint(BaseModel):
    date: str
    orders: int
    paid_orders: int
    gross_sales: Decimal
    refunds: Decimal
    net_sales: Decimal
    contribution_before_cac: Decimal | None


class AnalyticsExportRow(BaseModel):
    order_number: str
    order_date: str
    payment_date: str | None
    product: str
    variant: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    shipping: Decimal
    payment_status: str
    refund_status: str | None
    refund_amount: Decimal | None
    fulfillment_status: str
    supplier_cost: Decimal | None
    shipping_cost: Decimal | None
    contribution: Decimal | None
    data_quality: str


class OrderProfitabilityDTO(BaseModel):
    order_id: UUID
    order_number: str
    payment_status: str
    refund_status: str | None
    gross_sales: Decimal
    refunds: Decimal
    net_sales: Decimal
    product_cost: MetricAvailability
    shipping_cost: MetricAvailability
    payment_fees: MetricAvailability
    contribution_before_cac: MetricAvailability
    contribution_margin_percent: Decimal | None
    contribution_status: str
    actual_cac: MetricAvailability
    contribution_after_cac: MetricAvailability
    missing: list[str]
