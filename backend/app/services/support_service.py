from __future__ import annotations

import logging
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.entities import SupportTicket
from app.schemas.support import FaqItemDTO, FaqListResponse, SupportTicketRequest, SupportTicketResponse

_FAQ_ITEMS: list[FaqItemDTO] = [
    FaqItemDTO(
        question="How does LeTrusto's AI recommendation work?",
        answer="Our AI analyses your budget, usage patterns, and preferences to suggest the best products. It considers category, performance, battery life, camera quality, and value for money.",
        category="AI",
    ),
    FaqItemDTO(
        question="Are the prices shown on LeTrusto accurate?",
        answer="Prices are indicative and updated periodically. Always verify the final price on the retailer's website before purchase.",
        category="Pricing",
    ),
    FaqItemDTO(
        question="How do I set up a price alert?",
        answer="Log in to your account, open any product page, and click 'Notify Me'. You can set a target price and we'll alert you when it drops.",
        category="Price Alerts",
    ),
    FaqItemDTO(
        question="How do I compare products?",
        answer="Click the 'Compare' button on any product card or visit the Compare page to add up to 4 products for a side-by-side comparison.",
        category="Comparison",
    ),
    FaqItemDTO(
        question="Can I save my favourites?",
        answer="Yes! Click the heart icon on any product to add it to your favourites. Favourites are saved to your account when logged in.",
        category="Favourites",
    ),
    FaqItemDTO(
        question="How do I report incorrect product information?",
        answer="Use the 'Report Wrong Information' option in the Support section. Our team reviews all reports within 48 hours.",
        category="Reporting",
    ),
    FaqItemDTO(
        question="Does LeTrusto sell products directly?",
        answer="No. LeTrusto is a product discovery and comparison platform. We link to trusted retailers like Amazon, Flipkart, Croma, and others.",
        category="General",
    ),
    FaqItemDTO(
        question="How do I delete my account?",
        answer="Go to Dashboard → Settings → Delete Account. All your data will be permanently removed within 30 days.",
        category="Account",
    ),
]

logger = logging.getLogger(__name__)


class SupportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_faq(self) -> FaqListResponse:
        return FaqListResponse(items=_FAQ_ITEMS)

    def create_ticket(self, req: SupportTicketRequest, user_id: uuid.UUID | None = None) -> SupportTicketResponse:
        try:
            ticket = SupportTicket(
                user_id=user_id,
                email=req.email,
                category=req.category,
                subject=req.subject,
                body=req.body,
            )
            self.db.add(ticket)
            self.db.commit()
            self.db.refresh(ticket)
            return SupportTicketResponse(
                id=ticket.id,
                status=ticket.status,
                message="Your support ticket has been received. We'll get back to you within 24-48 hours.",
            )
        except Exception:
            self.db.rollback()
            logger.exception("Failed to create support ticket", extra={"category": req.category})
            raise HTTPException(
                status_code=500,
                detail="We could not create your support ticket right now. Please try again shortly.",
            )
