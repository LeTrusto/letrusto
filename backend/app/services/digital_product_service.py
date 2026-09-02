from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID

import razorpay
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.entities import DigitalEntitlement, DigitalPaymentAttempt, User
from app.schemas.digital_products import DigitalPaymentOrderDTO, DigitalPaymentVerification, DigitalPurchaseDTO

PRODUCTS = {
    "small-business-finance-pricing-toolkit": {"amount": Decimal("499.00"), "currency": "INR", "filename": "small-business-finance-pricing-toolkit.csv"},
    "freelancer-rate-project-pricing-toolkit": {"amount": Decimal("399.00"), "currency": "INR", "filename": "freelancer-rate-project-pricing-toolkit.csv"},
    "freelancer-agency-client-work-workbook": {"amount": Decimal("599.00"), "currency": "INR", "filename": "freelancer-agency-client-work-workbook.csv"},
}
ASSET_ROOT = Path(__file__).resolve().parents[2] / "content" / "digital-products"


class DigitalProductService:
    provider = "RAZORPAY"

    def __init__(self, db: Session, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings or get_settings()

    def _product(self, slug: str) -> dict[str, object]:
        product = PRODUCTS.get(slug)
        if product is None:
            raise HTTPException(status_code=404, detail="Digital product not found")
        return product

    def _client(self):
        if not self.settings.RAZORPAY_KEY_ID or not self.settings.RAZORPAY_KEY_SECRET:
            raise HTTPException(status_code=503, detail="Digital checkout is not configured")
        return razorpay.Client(auth=(self.settings.RAZORPAY_KEY_ID, self.settings.RAZORPAY_KEY_SECRET))

    def create_payment_order(self, user: User, slug: str) -> DigitalPaymentOrderDTO:
        product = self._product(slug)
        existing = self.db.scalar(select(DigitalPaymentAttempt).where(
            DigitalPaymentAttempt.user_id == user.id,
            DigitalPaymentAttempt.product_slug == slug,
            DigitalPaymentAttempt.status == "PENDING",
        ).order_by(DigitalPaymentAttempt.created_at.desc()))
        if existing:
            provider_order_id = existing.provider_order_id
        else:
            amount = int(Decimal(product["amount"]) * 100)
            try:
                provider_order = self._client().order.create({
                    "amount": amount,
                    "currency": product["currency"],
                    "receipt": f"digital-{user.id}-{slug}"[:40],
                    "notes": {"letrusto_product_slug": slug, "letrusto_user_id": str(user.id)},
                })
            except Exception as exc:
                raise HTTPException(status_code=502, detail="Digital payment order could not be created") from exc
            provider_order_id = str(provider_order.get("id") or "")
            if not provider_order_id:
                raise HTTPException(status_code=502, detail="Payment provider returned no order ID")
            existing = DigitalPaymentAttempt(
                user_id=user.id, product_slug=slug, provider=self.provider,
                provider_order_id=provider_order_id, amount=product["amount"], currency=product["currency"],
            )
            self.db.add(existing)
            self.db.commit()
            self.db.refresh(existing)
        return DigitalPaymentOrderDTO(attempt_id=existing.id, product_slug=slug, provider=self.provider, key_id=self.settings.RAZORPAY_KEY_ID, razorpay_order_id=provider_order_id, amount=int(Decimal(product["amount"]) * 100), currency=str(product["currency"]))

    def verify_payment(self, user: User, slug: str, payload: DigitalPaymentVerification) -> DigitalPurchaseDTO:
        product = self._product(slug)
        attempt = self.db.scalar(select(DigitalPaymentAttempt).where(
            DigitalPaymentAttempt.user_id == user.id,
            DigitalPaymentAttempt.product_slug == slug,
            DigitalPaymentAttempt.provider_order_id == payload.razorpay_order_id,
        ).with_for_update())
        if attempt is None:
            raise HTTPException(status_code=404, detail="Digital payment attempt not found")
        if attempt.status == "VERIFIED":
            if attempt.provider_payment_id != payload.razorpay_payment_id:
                raise HTTPException(status_code=409, detail="Payment attempt already has a different payment")
            return self._purchase(attempt, slug)
        if attempt.provider_payment_id and attempt.provider_payment_id != payload.razorpay_payment_id:
            raise HTTPException(status_code=409, detail="Payment attempt already has a different payment")
        try:
            client = self._client()
            provider_order = client.order.fetch(payload.razorpay_order_id)
            payment = client.payment.fetch(payload.razorpay_payment_id)
            client.utility.verify_payment_signature({"razorpay_order_id": payload.razorpay_order_id, "razorpay_payment_id": payload.razorpay_payment_id, "razorpay_signature": payload.razorpay_signature})
        except Exception as exc:
            raise HTTPException(status_code=422, detail="Invalid digital payment signature or payment details") from exc
        expected = int(Decimal(product["amount"]) * 100)
        if (str(provider_order.get("id") or "") != payload.razorpay_order_id or int(provider_order.get("amount") or 0) != expected or str(provider_order.get("currency") or "") != product["currency"] or str(payment.get("order_id") or "") != payload.razorpay_order_id or int(payment.get("amount") or 0) != expected or str(payment.get("currency") or "") != product["currency"] or str(payment.get("status") or "").lower() != "captured"):
            raise HTTPException(status_code=422, detail="Digital payment does not match the product")
        attempt.provider_payment_id = payload.razorpay_payment_id
        attempt.status = "VERIFIED"
        entitlement = self.db.scalar(select(DigitalEntitlement).where(DigitalEntitlement.user_id == user.id, DigitalEntitlement.product_slug == slug).with_for_update())
        if entitlement is None:
            self.db.add(DigitalEntitlement(user_id=user.id, payment_attempt_id=attempt.id, product_slug=slug))
        self.db.commit()
        return self._purchase(attempt, slug)

    def _purchase(self, attempt: DigitalPaymentAttempt, slug: str) -> DigitalPurchaseDTO:
        return DigitalPurchaseDTO(product_slug=slug, status="verified", download_url=f"/digital-products/{slug}/download", amount=attempt.amount, currency=attempt.currency)

    def download_path(self, user: User, slug: str) -> tuple[Path, DigitalEntitlement]:
        self._product(slug)
        entitlement = self.db.scalar(select(DigitalEntitlement).where(DigitalEntitlement.user_id == user.id, DigitalEntitlement.product_slug == slug).with_for_update())
        if entitlement is None:
            raise HTTPException(status_code=403, detail="Digital purchase required")
        path = ASSET_ROOT / str(PRODUCTS[slug]["filename"])
        if not path.is_file():
            raise HTTPException(status_code=503, detail="Digital file is temporarily unavailable")
        entitlement.download_count += 1
        entitlement.last_downloaded_at = datetime.now(timezone.utc)
        self.db.commit()
        return path, entitlement
