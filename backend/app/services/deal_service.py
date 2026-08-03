from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.entities import Deal, Product
from app.schemas.deal import DealDTO, DealsResponse


def _deal_to_dto(deal: Deal) -> DealDTO:
    product = deal.product
    image = product.images[0].url if product.images else None
    return DealDTO(
        id=deal.id,
        product_id=str(product.id),
        product_name=product.name,
        product_slug=product.slug,
        product_image=image,
        current_price=float(product.price_value),
        currency=product.currency,
        deal_type=deal.deal_type,
        label=deal.label,
        discount_percent=deal.discount_percent,
        coupon_code=deal.coupon_code,
        cashback_amount=float(deal.cashback_amount) if deal.cashback_amount else None,
        valid_until=deal.valid_until.isoformat() if deal.valid_until else None,
    )


class DealService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_deals(self) -> DealsResponse:
        now = datetime.now(timezone.utc)
        active = (
            self.db.query(Deal)
            .filter(Deal.is_active.is_(True))
            .filter((Deal.valid_until.is_(None)) | (Deal.valid_until > now))
            .join(Deal.product)
            .all()
        )
        today = [_deal_to_dto(d) for d in active if d.deal_type == "today"]
        festival = [_deal_to_dto(d) for d in active if d.deal_type == "festival"]
        cashback = [_deal_to_dto(d) for d in active if d.deal_type == "cashback"]
        coupon = [_deal_to_dto(d) for d in active if d.deal_type == "coupon"]
        trending = [_deal_to_dto(d) for d in active if d.deal_type == "trending"]
        ai_recommended = [_deal_to_dto(d) for d in active if d.deal_type == "ai_recommended"]
        return DealsResponse(
            today_deals=today,
            festival_offers=festival,
            cashback_deals=cashback,
            coupon_deals=coupon,
            trending=trending,
            ai_recommended=ai_recommended,
        )

    # ── Fallback: derive deals from top-rated products when DB is empty ───────
    def get_deals_with_fallback(self) -> DealsResponse:
        deals = self.get_deals()
        total = (
            len(deals.today_deals) + len(deals.festival_offers) +
            len(deals.cashback_deals) + len(deals.coupon_deals) +
            len(deals.trending) + len(deals.ai_recommended)
        )
        if total > 0:
            return deals
        return self._derive_deals_from_products()

    def _derive_deals_from_products(self) -> DealsResponse:
        products = (
            self.db.query(Product)
            .order_by(Product.ai_score.desc())
            .limit(30)
            .all()
        )

        def _make(p: Product, deal_type: str, discount: int, label: str) -> DealDTO:
            image = p.images[0].url if p.images else None
            return DealDTO(
                id=0,
                product_id=str(p.id),
                product_name=p.name,
                product_slug=p.slug,
                product_image=image,
                current_price=float(p.price_value),
                currency=p.currency,
                deal_type=deal_type,
                label=label,
                discount_percent=discount,
                coupon_code=None,
                cashback_amount=None,
                valid_until=None,
            )

        today_deals = [_make(p, "today", 10 + i * 2, "Today's Pick") for i, p in enumerate(products[:6])]
        trending = [_make(p, "trending", 5, "Trending Now") for p in products[6:12]]
        ai_recommended = [_make(p, "ai_recommended", 8, "AI Recommended") for p in products[12:18]]
        festival = [_make(p, "festival", 15, "Festival Offer") for p in products[18:22]]
        cashback_deals = [_make(p, "cashback", 0, "Cashback Available") for p in products[22:26]]
        coupon_deals = [_make(p, "coupon", 12, "Coupon Deal") for p in products[26:30]]

        return DealsResponse(
            today_deals=today_deals,
            festival_offers=festival,
            cashback_deals=cashback_deals,
            coupon_deals=coupon_deals,
            trending=trending,
            ai_recommended=ai_recommended,
        )
