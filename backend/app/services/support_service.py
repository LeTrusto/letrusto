from __future__ import annotations

import logging
from datetime import UTC
import uuid
from typing import Any

from fastapi import HTTPException
from fastapi import Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.entities import SupportTicket
from app.schemas.support import FaqItemDTO, FaqListResponse, SupportTicketRequest, SupportTicketResponse
from app.services.email_service import EmailService

PRIORITY_BY_CATEGORY: dict[str, str] = {
    "contact": "Normal",
    "feedback": "Low",
    "report_wrong": "High",
    "report_broken": "High",
    "service_enquiry": "Normal",
    "other": "Normal",
}

SERVICE_SLUGS = frozenset({
    "website-setup",
    "landing-page",
    "business-website",
    "website-redesign",
    "ecommerce-setup",
    "whatsapp-business-integrations",
    "automation",
    "dashboards",
    "custom-business-tools",
})

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
    def __init__(
        self,
        db: Session,
        *,
        email_service: EmailService | None = None,
        support_email: str | None = None,
        from_email: str | None = None,
        website_url: str = "https://letrusto.com",
    ) -> None:
        self.db = db
        settings = get_settings()
        self.email_service = email_service or EmailService.from_settings(settings)
        self.support_email = support_email or settings.SUPPORT_EMAIL
        self.from_email = from_email or settings.FROM_EMAIL
        self.website_url = website_url

    def get_faq(self) -> FaqListResponse:
        return FaqListResponse(items=_FAQ_ITEMS)

    def create_ticket(
        self,
        req: SupportTicketRequest,
        user_id: uuid.UUID | None = None,
        customer_name: str | None = None,
        request: Request | None = None,
    ) -> SupportTicketResponse:
        if req.category == "service_enquiry" and req.service_slug not in SERVICE_SLUGS:
            raise HTTPException(status_code=422, detail="Choose a valid service before submitting an enquiry.")
        if req.category != "service_enquiry" and req.service_slug is not None:
            raise HTTPException(status_code=422, detail="Service details are only valid for service enquiries.")
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

            logger.info(
                "Support ticket saved",
                extra={"ticket_id": ticket.id, "category": ticket.category, "email": ticket.email},
            )

            email_context = self._build_email_context(
                ticket=ticket,
                req=req,
                customer_name=customer_name,
                request=request,
            )
            self._send_support_emails(ticket.id, req.email, email_context)

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

    def _send_support_emails(
        self,
        ticket_id: int,
        customer_email: str,
        context: dict[str, Any],
    ) -> None:
        try:
            self.email_service.send_template(
                "support_ticket_admin",
                to=self.support_email,
                context=context,
                reply_to=customer_email,
                from_email=self.from_email,
            )
            logger.info("Admin support email sent", extra={"ticket_id": ticket_id, "recipient": self.support_email})
        except Exception:
            logger.exception("Failed to send admin support email", extra={"ticket_id": ticket_id})

        try:
            self.email_service.send_template(
                "support_ticket_customer_confirmation",
                to=customer_email,
                context=context,
                reply_to=self.support_email,
                from_email=self.from_email,
            )
            logger.info(
                "Customer support confirmation email sent",
                extra={"ticket_id": ticket_id, "recipient": customer_email},
            )
        except Exception:
            logger.exception("Failed to send customer support confirmation email", extra={"ticket_id": ticket_id})

    def _build_email_context(
        self,
        *,
        ticket: SupportTicket,
        req: SupportTicketRequest,
        customer_name: str | None,
        request: Request | None,
    ) -> dict[str, Any]:
        created = ticket.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)

        browser, platform, ip = self._extract_request_metadata(request)
        resolved_name = customer_name or req.customer_name or self._derive_customer_name(req.email)

        return {
            "ticket_id": ticket.id,
            "customer_name": resolved_name,
            "customer_email": req.email,
            "subject": req.subject,
            "category": req.category,
            "priority": PRIORITY_BY_CATEGORY.get(req.category, "Normal"),
            "message": req.body,
            "created_time": created.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC"),
            "browser": browser,
            "platform": platform,
            "ip": ip,
            "support_email": self.support_email,
            "website_url": self.website_url,
            "logo_url": "https://letrusto.com/images/logo/logo.png",
        }

    @staticmethod
    def _derive_customer_name(email: str) -> str:
        local_part = email.split("@", 1)[0].strip()
        if not local_part:
            return "LeTrusto Customer"
        return local_part.replace(".", " ").replace("_", " ").title()

    @staticmethod
    def _extract_request_metadata(request: Request | None) -> tuple[str, str, str]:
        if request is None:
            return ("Unknown", "Unknown", "Not available")

        headers = request.headers
        user_agent = headers.get("user-agent", "")
        browser = SupportService._parse_browser(user_agent)
        platform = SupportService._parse_platform(headers.get("sec-ch-ua-platform"), user_agent)
        ip = SupportService._extract_ip(request)
        return browser, platform, ip

    @staticmethod
    def _extract_ip(request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if forwarded_for:
            return forwarded_for
        client = request.client
        if client and client.host:
            return client.host
        return "Not available"

    @staticmethod
    def _parse_browser(user_agent: str) -> str:
        ua = user_agent.lower()
        if "edg/" in ua:
            return "Microsoft Edge"
        if "chrome/" in ua and "chromium" not in ua:
            return "Google Chrome"
        if "firefox/" in ua:
            return "Mozilla Firefox"
        if "safari/" in ua and "chrome/" not in ua:
            return "Safari"
        if user_agent:
            return "Unknown Browser"
        return "Unknown"

    @staticmethod
    def _parse_platform(platform_hint: str | None, user_agent: str) -> str:
        if platform_hint:
            return platform_hint.strip('"') or "Unknown"

        ua = user_agent.lower()
        if "windows" in ua:
            return "Windows"
        if "mac os" in ua or "macintosh" in ua:
            return "macOS"
        if "android" in ua:
            return "Android"
        if "iphone" in ua or "ipad" in ua or "ios" in ua:
            return "iOS"
        if "linux" in ua:
            return "Linux"
        return "Unknown"
