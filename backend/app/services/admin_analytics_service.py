import csv
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from io import StringIO
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models.entities import InventoryReservation, Order, Product, ProductVariant, RefundRequest
from app.services.marketing_service import MarketingAnalyticsContext, MarketingService
from app.schemas.admin_analytics import (
    AnalyticsExportRow,
    AnalyticsPeriod,
    AnalyticsSummary,
    InventoryAnalyticsDTO,
    MetricAvailability,
    ProductPerformanceDTO,
    OrderProfitabilityDTO,
    SalesTrendPoint,
    VariantPerformanceDTO,
)

CENT = Decimal("0.01")


class AdminAnalyticsService:
    """Read-only operational and accounting foundation over authoritative records."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    @staticmethod
    def resolve_period(period: str = "last_30_days", start_date: date | None = None, end_date: date | None = None) -> AnalyticsPeriod:
        today = datetime.now(timezone.utc).date()
        if period == "today":
            start, end, label = today, today + timedelta(days=1), "Today"
        elif period == "yesterday":
            start, end, label = today - timedelta(days=1), today, "Yesterday"
        elif period == "last_7_days":
            start, end, label = today - timedelta(days=6), today + timedelta(days=1), "Last 7 days"
        elif period == "this_month":
            start, end, label = today.replace(day=1), today + timedelta(days=1), "This month"
        elif period == "previous_month":
            first_this = today.replace(day=1)
            previous_end = first_this
            previous_start = (first_this - timedelta(days=1)).replace(day=1)
            start, end, label = previous_start, previous_end, "Previous month"
        elif period == "custom":
            if start_date is None or end_date is None:
                raise ValueError("Custom reporting period requires start_date and end_date")
            if end_date < start_date:
                raise ValueError("end_date must not be before start_date")
            start, end, label = start_date, end_date + timedelta(days=1), "Custom"
        else:
            start, end, label = today - timedelta(days=29), today + timedelta(days=1), "Last 30 days"
        return AnalyticsPeriod(label=label, start=datetime.combine(start, time.min, timezone.utc), end=datetime.combine(end, time.min, timezone.utc))

    @staticmethod
    def _unknown(reason: str) -> MetricAvailability:
        return MetricAvailability(value=None, status="NOT_AVAILABLE", reason=reason)

    def _snapshot_costs(self, items) -> tuple[Decimal | None, Decimal | None, list[str]]:
        product_cost = Decimal("0")
        shipping_cost = Decimal("0")
        missing: list[str] = []
        for item in items:
            if item.supplier_cost_inr_snapshot is None:
                missing.append("historical_supplier_cost")
            else:
                product_cost += item.supplier_cost_inr_snapshot * item.quantity
            if item.shipping_cost_inr_snapshot is None:
                missing.append("historical_shipping_cost")
            else:
                shipping_cost += item.shipping_cost_inr_snapshot * item.quantity
        return (
            self._quantize(product_cost) if "historical_supplier_cost" not in missing else None,
            self._quantize(shipping_cost) if "historical_shipping_cost" not in missing else None,
            sorted(set(missing)),
        )

    def _contribution_metric(self, net_sales: Decimal, items) -> tuple[MetricAvailability, MetricAvailability, MetricAvailability, Decimal | None, str, list[str]]:
        product_cost, shipping_cost, missing = self._snapshot_costs(items)
        missing = [*missing, "actual_payment_fee"]
        if product_cost is None and shipping_cost is None:
            return self._unknown("Historical product and shipping costs are unavailable"), self._unknown("Historical shipping cost is unavailable"), self._unknown("Required historical economics are unavailable"), None, "UNKNOWN", sorted(set(missing))
        known = net_sales - (product_cost or Decimal("0")) - (shipping_cost or Decimal("0"))
        contribution = MetricAvailability(value=self._quantize(known), status="PARTIAL", reason="Actual Cashfree payment fee is not stored")
        margin = self._quantize(known * Decimal("100") / net_sales) if net_sales > 0 else None
        product_metric = MetricAvailability(value=product_cost, status="COMPLETE" if product_cost is not None else "UNKNOWN", reason=None if product_cost is not None else "Historical supplier cost is unavailable")
        shipping_metric = MetricAvailability(value=shipping_cost, status="COMPLETE" if shipping_cost is not None else "UNKNOWN", reason=None if shipping_cost is not None else "Historical shipping cost is unavailable")
        return product_metric, shipping_metric, contribution, margin, "PARTIAL", sorted(set(missing))

    def _cac_metric(self, value: Decimal | None, status: str, reason: str) -> MetricAvailability:
        return MetricAvailability(value=self._quantize(value) if value is not None else None, status=status, reason=None if value is not None else reason)

    def _after_cac(self, contribution: MetricAvailability, cac_amount: Decimal | None, cac_status: str, net_sales: Decimal) -> tuple[MetricAvailability, Decimal | None, str]:
        if contribution.value is None:
            return self._unknown("Contribution before CAC is unavailable"), None, "UNKNOWN"
        if cac_amount is None:
            return self._unknown("Actual CAC is not attributed"), None, cac_status
        value = self._quantize(contribution.value - cac_amount)
        margin = self._quantize(value * Decimal("100") / net_sales) if net_sales > 0 else None
        return MetricAvailability(value=value, status="PARTIAL", reason="Actual Cashfree payment fee is not stored"), margin, "PARTIAL"

    @staticmethod
    def _order_cac_status(order: Order, context: MarketingAnalyticsContext) -> str:
        if not order.paid_at or order.payment_status != "PAID":
            return "UNKNOWN"
        return context.order_status.get(order.id, "NOT_ATTRIBUTED")

    def _marketing_context(self, period: AnalyticsPeriod, paid_orders: list[Order]) -> MarketingAnalyticsContext:
        return MarketingService(self.db).analytics_context(period.start, period.end, paid_orders)

    @staticmethod
    def _quantize(value: Decimal) -> Decimal:
        return value.quantize(CENT, rounding=ROUND_HALF_UP)

    def _orders(self, period: AnalyticsPeriod) -> list[Order]:
        return list(self.db.scalars(
            select(Order).where(Order.created_at >= period.start, Order.created_at < period.end).options(
                selectinload(Order.items), selectinload(Order.refund_requests)
            )
        ).all())

    def _paid_orders(self, period: AnalyticsPeriod) -> list[Order]:
        return list(self.db.scalars(
            select(Order).where(Order.paid_at >= period.start, Order.paid_at < period.end, Order.paid_at.is_not(None)).options(
                selectinload(Order.items), selectinload(Order.refund_requests)
            )
        ).all())

    def _successful_refunds(self, period: AnalyticsPeriod) -> list[RefundRequest]:
        return list(self.db.scalars(select(RefundRequest).where(
            RefundRequest.status == "SUCCESS",
            RefundRequest.completed_at >= period.start,
            RefundRequest.completed_at < period.end,
        )).all())

    def summary(self, period: AnalyticsPeriod) -> AnalyticsSummary:
        orders = self._orders(period)
        paid_orders = self._paid_orders(period)
        refunds = self._successful_refunds(period)
        gross = sum((order.total for order in orders), Decimal("0"))
        paid = sum((order.total for order in paid_orders), Decimal("0"))
        refunded = sum((refund.amount for refund in refunds), Decimal("0"))
        net_sales = paid - refunded
        paid_items = [item for order in paid_orders for item in order.items]
        product_cost_metric, shipping_cost_metric, contribution_metric, contribution_margin, contribution_status, _ = self._contribution_metric(net_sales, paid_items)
        marketing = self._marketing_context(period, paid_orders)
        attributed_orders = [order for order in paid_orders if order.id in marketing.attributed_orders]
        attributed_refunds = {refund.order_id: refund.amount for refund in refunds if refund.order_id in marketing.attributed_orders}
        after_total = Decimal("0")
        after_sales = Decimal("0")
        known_after = 0
        for order in attributed_orders:
            order_net_sales = order.total - attributed_refunds.get(order.id, Decimal("0"))
            order_contribution = self._contribution_metric(order_net_sales, order.items)[2]
            if order_contribution.value is not None:
                after_total += order_contribution.value - marketing.order_cac[order.id]
                after_sales += order_net_sales
                known_after += 1
        attributed_cac = self._cac_metric(marketing.attributed_cac, marketing.actual_cac_status, "No paid orders have both attribution and matching marketing spend")
        blended_cac = self._cac_metric(marketing.blended_cac, "BLENDED" if marketing.blended_cac is not None else "NOT_CONFIGURED", "No paid orders or marketing spend are available")
        contribution_after = MetricAvailability(value=self._quantize(after_total), status="PARTIAL", reason="Only attributed orders with known historical costs are included") if known_after else self._unknown("No attributed orders have calculable contribution")
        status_breakdown = defaultdict(int)
        for order in orders:
            status_breakdown[f"payment:{order.payment_status}"] += 1
            status_breakdown[f"fulfillment:{order.fulfillment_status}"] += 1
        paid_average = self._quantize(paid / len(paid_orders)) if paid_orders else None
        return AnalyticsSummary(
            period=period,
            gross_order_value=self._quantize(gross),
            paid_sales=self._quantize(paid),
            refunded_amount=self._quantize(refunded),
            net_sales=self._quantize(net_sales),
            payment_fees=self._unknown("Actual Cashfree fee data is not stored"),
            landed_cost=product_cost_metric,
            shipping_cost=shipping_cost_metric,
            contribution_before_cac=contribution_metric,
            cac=attributed_cac,
            contribution_after_cac=contribution_after,
            marketing_spend=self._quantize(marketing.spend),
            attributed_orders=len(marketing.attributed_orders),
            attributed_sales=self._quantize(marketing.attributed_sales),
            attributed_cac=attributed_cac,
            blended_cac=blended_cac,
            roas=self._cac_metric(marketing.roas, "ATTRIBUTED" if marketing.roas is not None else "NOT_CONFIGURED", "No attributed spend and sales are available"),
            contribution_after_cac_status=contribution_after.status,
            order_count=len(orders),
            paid_order_count=len(paid_orders),
            refunded_order_count=len({refund.order_id for refund in refunds}),
            pending_payment_count=sum(1 for order in orders if order.payment_status == "PENDING"),
            average_order_value=paid_average,
            status_breakdown=dict(status_breakdown),
            policy_assumptions={
                "fx_rate_usd_to_inr": self.settings.PRICING_FX_RATE,
                "gateway_fee_percent": self.settings.PAYMENT_GATEWAY_PCT,
                "rto_reserve_percent": self.settings.RTO_RESERVE_PCT,
                "target_contribution_margin_percent": self.settings.TARGET_CONTRIBUTION_MARGIN_PCT,
                "target_cac_inr": self.settings.TARGET_CAC_INR,
            },
            contribution_status=contribution_status,
            contribution_margin_percent=contribution_margin,
        )

    def _current_variant_map(self, ids: set[UUID]) -> dict[UUID, ProductVariant]:
        if not ids:
            return {}
        variants = list(self.db.scalars(select(ProductVariant).where(ProductVariant.id.in_(ids)).options(selectinload(ProductVariant.product))).all())
        return {variant.id: variant for variant in variants}

    def _refund_allocations(self, orders: list[Order]) -> dict[UUID, Decimal]:
        allocations: dict[UUID, Decimal] = defaultdict(Decimal)
        for order in orders:
            successful = [refund for refund in order.refund_requests if refund.status == "SUCCESS"]
            refund_total = sum((refund.amount for refund in successful), Decimal("0"))
            if refund_total <= 0 or order.total <= 0:
                continue
            for item in order.items:
                allocations[item.id] += self._quantize(refund_total * item.line_total / order.total)
        return allocations

    def product_performance(self, period: AnalyticsPeriod) -> list[ProductPerformanceDTO]:
        orders = self._paid_orders(period)
        marketing = self._marketing_context(period, orders)
        refund_allocations = self._refund_allocations(orders)
        product_ids = {item.product_id for order in orders for item in order.items if item.product_id}
        products = {product.id: product for product in self.db.scalars(select(Product).where(Product.id.in_(product_ids))).all()} if product_ids else {}
        groups: dict[UUID | None, dict] = {}
        for order in orders:
            for item in order.items:
                group = groups.setdefault(item.product_id, {"name": item.product_name, "orders": set(), "units": 0, "sales": Decimal("0"), "refunds": Decimal("0"), "prices": []})
                group["orders"].add(order.id)
                group["units"] += item.quantity
                group["sales"] += item.line_total
                group["refunds"] += refund_allocations.get(item.id, Decimal("0"))
                group["prices"].append(item.unit_price)
        result = []
        for product_id, group in groups.items():
            product = products.get(product_id)
            net_sales = self._quantize(group["sales"] - group["refunds"])
            group_items = [item for order in orders for item in order.items if item.product_id == product_id]
            product_cost, shipping_cost, contribution, margin, contribution_status, missing = self._contribution_metric(net_sales, group_items)
            eligible_orders = [order for order in orders if order.id in marketing.order_cac and {item.product_id for item in order.items} == {product_id}]
            attributed_spend = sum((marketing.order_cac[order.id] for order in eligible_orders), Decimal("0"))
            actual_cac = attributed_spend / len(eligible_orders) if eligible_orders else None
            cac_status = "ATTRIBUTED" if eligible_orders else "NOT_ATTRIBUTED"
            cac_metric = self._cac_metric(actual_cac, cac_status, "No product-specific order attribution is available")
            spend_metric = self._cac_metric(attributed_spend if eligible_orders else None, cac_status, "No product-specific order attribution is available")
            after, after_margin, after_status = self._after_cac(contribution, attributed_spend if eligible_orders else None, cac_status, net_sales)
            quality = ["ACTUAL_PAYMENT_FEES_UNKNOWN", *missing]
            result.append(ProductPerformanceDTO(
                product_id=product_id,
                product_name=group["name"],
                orders=len(group["orders"]), units_sold=group["units"], paid_units=group["units"],
                gross_sales=self._quantize(group["sales"]), refunds=self._quantize(group["refunds"]), net_sales=net_sales,
                landed_cost=product_cost,
                shipping_cost=shipping_cost,
                contribution_before_cac=contribution,
                cac=cac_metric, actual_cac=cac_metric, attributed_marketing_spend=spend_metric, contribution_after_cac=after,
                average_selling_price=self._quantize(sum(group["prices"], Decimal("0")) / len(group["prices"])),
                inventory_available=product.cj_inventory if product else None,
                cj_inventory=product.cj_inventory if product else None,
                factory_inventory=product.factory_inventory if product else None,
                data_quality=quality if product else quality + ["CURRENT_PRODUCT_RECORD_UNAVAILABLE"],
                contribution_status=contribution_status,
                contribution_margin_percent=margin,
                contribution_after_cac_margin_percent=after_margin,
                cac_status=cac_status,
            ))
        return sorted(result, key=lambda item: item.net_sales, reverse=True)

    def variant_performance(self, period: AnalyticsPeriod) -> list[VariantPerformanceDTO]:
        orders = self._paid_orders(period)
        marketing = self._marketing_context(period, orders)
        refund_allocations = self._refund_allocations(orders)
        variant_ids = {item.variant_id for order in orders for item in order.items if item.variant_id}
        variants = self._current_variant_map(variant_ids)
        groups: dict[UUID | None, dict] = {}
        for order in orders:
            for item in order.items:
                group = groups.setdefault(item.variant_id, {"product_id": item.product_id, "product_name": item.product_name, "variant_name": item.variant_name, "orders": set(), "units": 0, "sales": Decimal("0"), "refunds": Decimal("0"), "prices": []})
                group["orders"].add(order.id); group["units"] += item.quantity; group["sales"] += item.line_total; group["refunds"] += refund_allocations.get(item.id, Decimal("0")); group["prices"].append(item.unit_price)
        result = []
        for variant_id, group in groups.items():
            variant = variants.get(variant_id)
            costs = self._contribution_metric(self._quantize(group["sales"] - group["refunds"]), [item for order in orders for item in order.items if item.variant_id == variant_id])
            eligible_orders = [order for order in orders if order.id in marketing.order_cac and {item.variant_id for item in order.items} == {variant_id}]
            attributed_spend = sum((marketing.order_cac[order.id] for order in eligible_orders), Decimal("0"))
            actual_cac = attributed_spend / len(eligible_orders) if eligible_orders else None
            cac_status = "ATTRIBUTED" if eligible_orders else "NOT_ATTRIBUTED"
            cac_metric = self._cac_metric(actual_cac, cac_status, "No variant-specific order attribution is available")
            spend_metric = self._cac_metric(attributed_spend if eligible_orders else None, cac_status, "No variant-specific order attribution is available")
            variant_net_sales = self._quantize(group["sales"] - group["refunds"])
            after, after_margin, after_status = self._after_cac(costs[2], attributed_spend if eligible_orders else None, cac_status, variant_net_sales)
            result.append(VariantPerformanceDTO(
                product_id=group["product_id"], product_name=group["product_name"], variant_id=variant_id, variant_name=group["variant_name"],
                supplier_variant_id=variant.supplier_variant_id if variant else None, supplier_variant_sku=variant.supplier_variant_sku if variant else None,
                orders=len(group["orders"]), units_sold=group["units"], paid_units=group["units"], gross_sales=self._quantize(group["sales"]), refunds=self._quantize(group["refunds"]), net_sales=self._quantize(group["sales"] - group["refunds"]),
                landed_cost=costs[0], shipping_cost=costs[1], contribution_before_cac=costs[2], cac=cac_metric, actual_cac=cac_metric, attributed_marketing_spend=spend_metric, contribution_after_cac=after, average_selling_price=self._quantize(sum(group["prices"], Decimal("0")) / len(group["prices"])), inventory_available=variant.cj_inventory if variant else None, cj_inventory=variant.cj_inventory if variant else None, factory_inventory=variant.factory_inventory if variant else None, data_quality=costs[5], contribution_status=costs[4], contribution_margin_percent=costs[3], contribution_after_cac_margin_percent=after_margin, cac_status=cac_status,
            ))
        return sorted(result, key=lambda item: item.net_sales, reverse=True)

    def inventory(self) -> list[InventoryAnalyticsDTO]:
        now = datetime.now(timezone.utc)
        variants = list(self.db.scalars(select(ProductVariant).options(selectinload(ProductVariant.product))).all())
        active = defaultdict(int)
        rows = self.db.execute(select(InventoryReservation.variant_id, func.coalesce(func.sum(InventoryReservation.quantity), 0)).where(InventoryReservation.status == "ACTIVE", InventoryReservation.expires_at > now).group_by(InventoryReservation.variant_id)).all()
        for variant_id, quantity in rows: active[variant_id] = int(quantity)
        result = []
        for variant in variants:
            cj = max(0, variant.cj_inventory or 0)
            available = max(0, cj - active[variant.id])
            result.append(InventoryAnalyticsDTO(product_id=variant.product_id, product_name=variant.product.name, variant_id=variant.id, variant_name=variant.name or variant.attributes, cj_inventory=variant.cj_inventory, factory_inventory=variant.factory_inventory, active_reservations=active[variant.id], available_customer_inventory=available, sellable_inventory_status="OUT_OF_STOCK" if cj == 0 else "LOW" if available <= 5 else "AVAILABLE"))
        return result

    def sales_trend(self, period: AnalyticsPeriod) -> list[SalesTrendPoint]:
        orders = self._orders(period); paid_orders = self._paid_orders(period); refunds = self._successful_refunds(period)
        marketing = self._marketing_context(period, paid_orders)
        refunds_by_order: dict[UUID, Decimal] = defaultdict(Decimal)
        for refund in refunds:
            refunds_by_order[refund.order_id] += refund.amount
        points = {current.date().isoformat(): {"orders": 0, "paid_orders": 0, "gross": Decimal("0"), "refunds": Decimal("0"), "contribution": Decimal("0"), "cac": Decimal("0"), "attributed": 0} for current in (period.start + timedelta(days=index) for index in range((period.end - period.start).days))}
        for order in orders: points[order.created_at.astimezone(timezone.utc).date().isoformat()]["orders"] += 1; points[order.created_at.astimezone(timezone.utc).date().isoformat()]["gross"] += order.total
        for order in paid_orders:
            key = order.paid_at.astimezone(timezone.utc).date().isoformat()
            points[key]["paid_orders"] += 1
            if order.id in marketing.order_cac:
                contribution = self._contribution_metric(order.total - refunds_by_order[order.id], order.items)[2]
                if contribution.value is not None:
                    points[key]["contribution"] += contribution.value
                    points[key]["cac"] += marketing.order_cac[order.id]
                    points[key]["attributed"] += 1
        for refund in refunds: points[refund.completed_at.astimezone(timezone.utc).date().isoformat()]["refunds"] += refund.amount
        return [SalesTrendPoint(date=key, orders=value["orders"], paid_orders=value["paid_orders"], gross_sales=self._quantize(value["gross"]), refunds=self._quantize(value["refunds"]), net_sales=self._quantize(value["gross"] - value["refunds"]), contribution_before_cac=self._quantize(value["contribution"]) if value["attributed"] else None, marketing_spend=self._quantize(marketing.spend_by_date.get(date.fromisoformat(key), Decimal("0"))), attributed_orders=value["attributed"], actual_cac=self._quantize(value["cac"] / value["attributed"]) if value["attributed"] else None, contribution_after_cac=self._quantize(value["contribution"] - value["cac"]) if value["attributed"] else None, cac_status="ATTRIBUTED" if value["attributed"] else "NOT_ATTRIBUTED") for key, value in sorted(points.items())]

    def export_rows(self, period: AnalyticsPeriod) -> list[AnalyticsExportRow]:
        rows = []
        paid_orders = self._paid_orders(period)
        marketing = self._marketing_context(period, paid_orders)
        for order in self._orders(period):
            refunds = [refund for refund in order.refund_requests if refund.status == "SUCCESS"]
            refund_amount = sum((refund.amount for refund in refunds), Decimal("0")) or None
            item_refunds = self._refund_allocations([order])
            gross_sales = order.total if order.payment_status == "PAID" and order.paid_at else Decimal("0")
            net_sales = gross_sales - (refund_amount or Decimal("0"))
            product_cost, shipping_cost, contribution, _, _, missing = self._contribution_metric(net_sales, order.items)
            cac_status = self._order_cac_status(order, marketing)
            actual_cac = marketing.order_cac.get(order.id)
            after, _, _ = self._after_cac(contribution, actual_cac, cac_status, net_sales)
            for item in order.items:
                rows.append(AnalyticsExportRow(order_number=order.order_number, order_date=order.created_at.isoformat(), payment_date=order.paid_at.isoformat() if order.payment_status == "PAID" and order.paid_at else None, product=item.product_name, variant=item.variant_name, quantity=item.quantity, unit_price=item.unit_price, line_total=item.line_total, shipping=order.shipping_amount, payment_status=order.payment_status, refund_status=refunds[0].status if refunds else None, refund_amount=item_refunds.get(item.id), fulfillment_status=order.fulfillment_status, supplier_cost=item.supplier_cost_inr_snapshot * item.quantity if item.supplier_cost_inr_snapshot is not None else None, shipping_cost=item.shipping_cost_inr_snapshot * item.quantity if item.shipping_cost_inr_snapshot is not None else None, contribution=contribution.value, marketing_spend=actual_cac, attributed_orders=1 if actual_cac is not None else 0, attributed_sales=order.total if actual_cac is not None else None, actual_cac=actual_cac, blended_cac=marketing.blended_cac, contribution_before_cac=contribution.value, contribution_after_cac=after.value, cac_status=cac_status, roas=marketing.roas if actual_cac is not None else None, data_quality="; ".join([*missing, "actual_payment_fee"] + ([] if actual_cac is not None else ["actual_cac"]))))
        return rows

    def export_csv(self, period: AnalyticsPeriod) -> str:
        output = StringIO(); writer = csv.DictWriter(output, fieldnames=list(AnalyticsExportRow.model_fields)); writer.writeheader(); writer.writerows([row.model_dump(mode="json") for row in self.export_rows(period)]); return output.getvalue()

    def order_profitability(self, order_id: UUID) -> OrderProfitabilityDTO:
        order = self.db.scalar(select(Order).where(Order.id == order_id).options(selectinload(Order.items), selectinload(Order.refund_requests)))
        if order is None:
            raise ValueError("Order not found")
        refunds = [refund for refund in order.refund_requests if refund.status == "SUCCESS"]
        gross = order.total if order.paid_at else Decimal("0")
        refunded = sum((refund.amount for refund in refunds), Decimal("0"))
        net_sales = gross - refunded
        product_cost, shipping_cost, contribution, margin, contribution_status, missing = self._contribution_metric(net_sales, order.items)
        payment_fees = self._unknown("Actual Cashfree payment fee is not stored")
        paid_orders = [order] if order.payment_status == "PAID" and order.paid_at else []
        context = MarketingService(self.db).analytics_context(order.paid_at, order.paid_at + timedelta(days=1), paid_orders) if paid_orders else None
        cac_status = self._order_cac_status(order, context) if context else "UNKNOWN"
        actual_cac = self._cac_metric(context.order_cac.get(order.id) if context else None, cac_status, "No matching attributed marketing spend is available")
        after, after_margin, profitability_status = self._after_cac(contribution, actual_cac.value, cac_status, net_sales)
        return OrderProfitabilityDTO(order_id=order.id, order_number=order.order_number, payment_status=order.payment_status, refund_status=refunds[0].status if refunds else None, gross_sales=self._quantize(gross), refunds=self._quantize(refunded), net_sales=self._quantize(net_sales), product_cost=product_cost, shipping_cost=shipping_cost, payment_fees=payment_fees, contribution_before_cac=contribution, contribution_margin_percent=margin, contribution_status=contribution_status, actual_cac=actual_cac, contribution_after_cac=after, contribution_after_cac_margin_percent=after_margin, cac_status=cac_status, profitability_status=profitability_status, missing=sorted(set([*missing, "actual_payment_fee"] + ([] if actual_cac.value is not None else ["actual_cac"]))))
