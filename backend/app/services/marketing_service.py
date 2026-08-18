from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from uuid import UUID
from dataclasses import dataclass
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.entities import MarketingSpend, Order, OrderMarketingAttribution
from app.schemas.marketing import AttributionCreate, AttributionDTO, MarketingCACResponse, MarketingCACRow, MarketingSpendCreate, MarketingSpendDTO

@dataclass
class MarketingAnalyticsContext:
    spend: Decimal
    attributed_orders: set[UUID]
    order_cac: dict[UUID, Decimal]
    order_status: dict[UUID, str]
    attributed_sales: Decimal
    attributed_cac: Decimal | None
    blended_cac: Decimal | None
    roas: Decimal | None
    actual_cac_status: str
    spend_by_date: dict[date, Decimal]

class MarketingService:
    def __init__(self, db: Session): self.db = db
    @staticmethod
    def periods(period="last_30_days", start_date=None, end_date=None):
        today=datetime.now(timezone.utc).date()
        if period == "today": start,end=today,today+timedelta(days=1)
        elif period == "yesterday": start,end=today-timedelta(days=1),today
        elif period == "last_7_days": start,end=today-timedelta(days=6),today+timedelta(days=1)
        elif period == "this_month": start,end=today.replace(day=1),today+timedelta(days=1)
        elif period == "previous_month":
            end=today.replace(day=1); start=(end-timedelta(days=1)).replace(day=1)
        elif period == "custom" and start_date and end_date: start,end=start_date,end_date+timedelta(days=1)
        else: start,end=today-timedelta(days=29),today+timedelta(days=1)
        return datetime.combine(start,time.min,timezone.utc),datetime.combine(end,time.min,timezone.utc)
    def create_spend(self, payload: MarketingSpendCreate):
        row=MarketingSpend(**payload.model_dump()); self.db.add(row); self.db.commit(); self.db.refresh(row); return self._spend_dto(row)
    def list_spend(self, start, end):
        return [self._spend_dto(x) for x in self.db.scalars(select(MarketingSpend).where(MarketingSpend.spend_date>=start.date(),MarketingSpend.spend_date<end.date()).order_by(MarketingSpend.spend_date.desc())).all()]
    def get_spend(self, spend_id):
        row=self.db.get(MarketingSpend,spend_id)
        if not row: raise NotFoundError("Marketing spend not found")
        return self._spend_dto(row)
    def update_spend(self, spend_id, payload):
        row=self.db.get(MarketingSpend,spend_id)
        if not row: raise NotFoundError("Marketing spend not found")
        for key,value in payload.model_dump().items(): setattr(row,key,value)
        self.db.commit(); self.db.refresh(row); return self._spend_dto(row)
    def delete_spend(self, spend_id):
        row=self.db.get(MarketingSpend,spend_id)
        if not row: raise NotFoundError("Marketing spend not found")
        self.db.delete(row); self.db.commit()
    def attribute(self,payload: AttributionCreate):
        order=self.db.get(Order,payload.order_id)
        if not order: raise NotFoundError("Order not found")
        if self.db.scalar(select(OrderMarketingAttribution).where(OrderMarketingAttribution.order_id==order.id)): raise BadRequestError("Order already has marketing attribution")
        row=OrderMarketingAttribution(**payload.model_dump(),status="ATTRIBUTED"); self.db.add(row); self.db.commit(); self.db.refresh(row); return AttributionDTO(id=row.id,order_id=row.order_id,channel=row.channel,campaign=row.campaign,attribution_method=row.attribution_method,status=row.status,created_at=row.created_at.isoformat())
    def cac(self,start,end):
        spend_rows=list(self.db.scalars(select(MarketingSpend).where(MarketingSpend.spend_date>=start.date(),MarketingSpend.spend_date<end.date())).all())
        spend=sum((x.spend_amount for x in spend_rows),Decimal("0"))
        attrs=list(self.db.scalars(select(OrderMarketingAttribution).where(OrderMarketingAttribution.status=="ATTRIBUTED")).all())
        order_ids=[x.order_id for x in attrs]
        orders={x.id:x for x in self.db.scalars(select(Order).where(Order.id.in_(order_ids),Order.payment_status=="PAID")).all()} if order_ids else {}
        paid_count=sum(1 for x in orders.values() if x.paid_at and start<=x.paid_at<end)
        rows=[]
        groups=sorted({(x.channel,x.campaign) for x in spend_rows} | {(x.channel,x.campaign) for x in attrs})
        attributed_total=0; attributed_spend=Decimal("0")
        for channel,campaign in groups:
            channel_spend=sum((x.spend_amount for x in spend_rows if x.channel==channel and x.campaign==campaign),Decimal("0")); channel_attrs=[x for x in attrs if x.channel==channel and x.campaign==campaign]; valid=[orders[x.order_id] for x in channel_attrs if x.order_id in orders and orders[x.order_id].paid_at and start<=orders[x.order_id].paid_at<end]; sales=sum((x.total for x in valid),Decimal("0")); cac=channel_spend/len(valid) if valid else None
            attributed_total += len(valid); attributed_spend += channel_spend if valid else Decimal("0")
            rows.append(MarketingCACRow(channel=channel,campaign=campaign,spend=channel_spend,attributed_orders=len(valid),attributed_sales=sales,attributed_cac=cac,blended_cac=channel_spend/paid_count if paid_count else None,roas=sales/channel_spend if channel_spend else None,cac_status="ATTRIBUTED" if valid else "NOT_ATTRIBUTED"))
        return MarketingCACResponse(spend=spend,attributed_orders=attributed_total,attributed_cac=attributed_spend/attributed_total if attributed_total else None,blended_cac=spend/paid_count if paid_count else None,target_cac=get_settings().TARGET_CAC_INR,actual_cac_status="ATTRIBUTED" if attributed_total else "NOT_CONFIGURED",rows=rows)
    def analytics_context(self, start: datetime, end: datetime, paid_orders: list[Order]) -> MarketingAnalyticsContext:
        spend_rows = list(self.db.scalars(select(MarketingSpend).where(MarketingSpend.spend_date >= start.date(), MarketingSpend.spend_date < end.date())).all())
        spend_by_group: dict[tuple[str, str | None], Decimal] = {}
        spend_by_date: dict[date, Decimal] = {}
        for row in spend_rows:
            key = (row.channel, row.campaign)
            spend_by_group[key] = spend_by_group.get(key, Decimal("0")) + row.spend_amount
            spend_by_date[row.spend_date] = spend_by_date.get(row.spend_date, Decimal("0")) + row.spend_amount
        paid_by_id = {order.id: order for order in paid_orders if order.paid_at and start <= order.paid_at < end}
        if not paid_by_id:
            return MarketingAnalyticsContext(sum(spend_by_group.values(), Decimal("0")), set(), {}, {}, Decimal("0"), None, None, None, "NOT_CONFIGURED", spend_by_date)
        attributions = list(self.db.scalars(select(OrderMarketingAttribution).where(OrderMarketingAttribution.order_id.in_(paid_by_id), OrderMarketingAttribution.status == "ATTRIBUTED")).all())
        groups: dict[tuple[str, str | None], list[UUID]] = {}
        for attribution in attributions:
            groups.setdefault((attribution.channel, attribution.campaign), []).append(attribution.order_id)
        order_cac: dict[UUID, Decimal] = {}
        order_status: dict[UUID, str] = {order_id: "NOT_ATTRIBUTED" for order_id in paid_by_id}
        attributed_sales = Decimal("0")
        attributed_spend = Decimal("0")
        for group, order_ids in groups.items():
            if group not in spend_by_group:
                for order_id in order_ids:
                    order_status[order_id] = "NOT_CONFIGURED"
                continue
            group_spend = spend_by_group[group]
            actual_cac = group_spend / len(order_ids)
            attributed_spend += group_spend
            for order_id in order_ids:
                order_cac[order_id] = actual_cac
                order_status[order_id] = "ATTRIBUTED"
                attributed_sales += paid_by_id[order_id].total
        spend = sum(spend_by_group.values(), Decimal("0"))
        attributed_count = len(order_cac)
        return MarketingAnalyticsContext(
            spend=spend,
            attributed_orders=set(order_cac),
            order_cac=order_cac,
            order_status=order_status,
            attributed_sales=attributed_sales,
            attributed_cac=attributed_spend / attributed_count if attributed_count else None,
            blended_cac=spend / len(paid_by_id) if paid_by_id else None,
            roas=attributed_sales / attributed_spend if attributed_spend else None,
            actual_cac_status="ATTRIBUTED" if attributed_count else ("NOT_CONFIGURED" if spend else "NOT_CONFIGURED"),
            spend_by_date=spend_by_date,
        )
    @staticmethod
    def _spend_dto(row): return MarketingSpendDTO(id=row.id,spend_date=row.spend_date,channel=row.channel,campaign=row.campaign,spend_amount=row.spend_amount,currency=row.currency,notes=row.notes,created_at=row.created_at.isoformat(),updated_at=row.updated_at.isoformat())
