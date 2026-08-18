import base64
import hashlib
import hmac
from datetime import datetime, timezone
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.entities import Order, PaymentAttempt, User
from app.schemas.payments import PaymentSessionDTO, PaymentStatusDTO
from app.services.fulfillment_service import FulfillmentService


class CashfreeService:
    def __init__(self, db: Session, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings or get_settings()

    @property
    def configured(self) -> bool:
        return bool(self.settings.CASHFREE_APP_ID and self.settings.CASHFREE_SECRET_KEY)

    @property
    def base_url(self) -> str:
        return "https://api.cashfree.com/pg" if self.settings.CASHFREE_ENV == "production" else "https://sandbox.cashfree.com/pg"

    def _headers(self, idempotency_key: str | None = None) -> dict[str, str]:
        headers = {
            "x-client-id": self.settings.CASHFREE_APP_ID,
            "x-client-secret": self.settings.CASHFREE_SECRET_KEY,
            "x-api-version": self.settings.CASHFREE_API_VERSION,
            "Content-Type": "application/json",
        }
        if idempotency_key:
            headers["x-idempotency-key"] = idempotency_key
        return headers

    def request_refund(self, provider_order_id: str, refund_amount, idempotency_key: str, reason: str) -> dict:
        if not self.configured:
            return {"configured": False, "provider_status": "PENDING", "failure_reason": "Cashfree credentials not configured"}

        payload = {
            "refund_amount": float(refund_amount),
            "refund_id": idempotency_key,
            "refund_note": reason or "Customer cancellation",
            "refund_speed": "STANDARD",
        }
        try:
            response = httpx.post(
                f"{self.base_url}/orders/{provider_order_id}/refunds",
                headers=self._headers(idempotency_key),
                json=payload,
                timeout=15,
            )
        except httpx.HTTPError as exc:
            return {"configured": True, "provider_status": "FAILED", "failure_reason": str(exc)[:500]}

        try:
            body = response.json()
        except ValueError:
            body = {}
        if response.status_code >= 300:
            return {
                "configured": True,
                "provider_status": "FAILED",
                "failure_reason": body.get("message") or f"HTTP {response.status_code}",
            }
        return {
            "configured": True,
            "provider_refund_id": body.get("cf_refund_id"),
            "provider_status": body.get("refund_status") or "PENDING",
            "provider_order_id": body.get("order_id") or provider_order_id,
        }

    def _order(self, user: User, order_id: UUID) -> Order:
        order = self.db.scalar(select(Order).where(Order.id == order_id, Order.user_id == user.id))
        if order is None:
            raise NotFoundError("Order not found")
        return order

    def create_session(self, user: User, order_id: UUID) -> PaymentSessionDTO:
        order = self._order(user, order_id)
        if order.status != "PENDING_PAYMENT" or order.payment_status in {"PAID", "REFUNDED", "CANCELLED"}:
            raise BadRequestError("Order is not payable")
        if not self.configured:
            raise BadRequestError("Cashfree sandbox credentials are not configured")
        if order.payment_session_id and order.payment_provider == "CASHFREE" and order.payment_status == "PENDING":
            return PaymentSessionDTO(order_id=order.id, provider="CASHFREE", provider_order_id=order.provider_order_id, payment_session_id=order.payment_session_id, amount=order.total, currency=order.currency)

        prior_attempts = list(self.db.scalars(select(PaymentAttempt).where(PaymentAttempt.order_id == order.id)).all())
        provider_order_id = order.order_number if not prior_attempts else f"{order.order_number}-R{len(prior_attempts) + 1}"
        return_url = self.settings.CASHFREE_RETURN_URL.format(order_id=order.id)
        payload = {
            "order_id": provider_order_id,
            "order_amount": float(order.total),
            "order_currency": order.currency,
            "customer_details": {
                "customer_id": str(user.id),
                "customer_name": order.customer_name,
                "customer_email": order.customer_email,
                "customer_phone": order.customer_phone,
            },
            "order_meta": {"return_url": return_url, "notify_url": self.settings.CASHFREE_NOTIFY_URL},
        }
        try:
            response = httpx.post(f"{self.base_url}/orders", headers=self._headers(order.order_number), json=payload, timeout=10)
        except httpx.HTTPError as exc:
            raise BadRequestError("Cashfree payment service is unavailable") from exc
        if response.status_code >= 400:
            raise BadRequestError("Cashfree payment session could not be created")
        body = response.json()
        session_id = body.get("payment_session_id")
        provider_id = body.get("order_id") or provider_order_id
        if not session_id:
            raise BadRequestError("Cashfree returned no payment session")
        order.payment_provider = "CASHFREE"
        order.provider_order_id = provider_id
        order.payment_session_id = session_id
        order.payment_attempted_at = datetime.now(timezone.utc)
        self.db.add(PaymentAttempt(provider="CASHFREE", provider_order_id=provider_id, session_id=session_id, order=order))
        self.db.commit()
        return PaymentSessionDTO(order_id=order.id, provider="CASHFREE", provider_order_id=provider_id, payment_session_id=session_id, amount=order.total, currency=order.currency)

    @staticmethod
    def verify_webhook_signature(raw_body: bytes, timestamp: str | None, signature: str | None, secret: str) -> bool:
        if not timestamp or not signature or not secret:
            return False
        expected = base64.b64encode(hmac.new(secret.encode(), timestamp.encode() + raw_body, hashlib.sha256).digest()).decode()
        return hmac.compare_digest(expected, signature)

    async def process_webhook(self, raw_body: bytes, timestamp: str | None, signature: str | None) -> None:
        secret = self.settings.CASHFREE_WEBHOOK_SECRET or self.settings.CASHFREE_SECRET_KEY
        if not self.verify_webhook_signature(raw_body, timestamp, signature, secret):
            raise BadRequestError("Invalid Cashfree webhook signature")
        body = __import__("json").loads(raw_body)
        data = body.get("data") or {}
        if body.get("type") == "REFUND_STATUS_WEBHOOK" and data.get("refund"):
            from app.services.cancellation_service import CancellationService

            refund = data["refund"]
            CancellationService(self.db).process_refund_webhook(
                provider_refund_id=str(refund.get("cf_refund_id") or ""),
                status=str(refund.get("refund_status") or ""),
                order_id_str=str(refund.get("order_id") or ""),
            )
            return
        provider_order_id = ((data.get("order") or {}).get("order_id"))
        payment = data.get("payment") or {}
        if not provider_order_id:
            raise BadRequestError("Cashfree webhook has no order ID")
        order = self.db.scalar(select(Order).where(Order.provider_order_id == provider_order_id))
        if order is None:
            raise NotFoundError("Cashfree order not found")
        status = payment.get("payment_status")
        provider_payment_id = str(payment.get("cf_payment_id")) if payment.get("cf_payment_id") is not None else None
        attempt = self.db.scalar(select(PaymentAttempt).where(PaymentAttempt.order_id == order.id, PaymentAttempt.provider_payment_id == provider_payment_id)) if provider_payment_id else None
        if attempt is None:
            attempt = PaymentAttempt(order=order, provider="CASHFREE", provider_order_id=provider_order_id, provider_payment_id=provider_payment_id, status=status or "PENDING")
            self.db.add(attempt)
        if order.payment_status == "PAID":
            self.db.commit()
            return
        attempt.status = status or attempt.status
        if status == "SUCCESS":
            order.payment_status = "PAID"
            order.status = "PAID"
            order.paid_at = order.paid_at or datetime.now(timezone.utc)
            order.provider_reference = provider_payment_id
        elif status in {"FAILED", "USER_DROPPED", "CANCELLED", "VOID"}:
            order.payment_status = "FAILED"
            order.payment_failure_reason = payment.get("payment_message") or status
        self.db.commit()
        if status == "SUCCESS":
            await FulfillmentService(self.db).submit(order.id)

    async def verify_payment(self, user: User, order_id: UUID) -> PaymentStatusDTO:
        order = self._order(user, order_id)
        if not self.configured or not order.provider_order_id:
            raise BadRequestError("Cashfree payment verification is not configured")
        response = httpx.get(f"{self.base_url}/orders/{order.provider_order_id}/payments", headers=self._headers(), timeout=10)
        if response.status_code >= 400:
            raise BadRequestError("Cashfree payment verification failed")
        payments = response.json()
        successful = next((item for item in payments if item.get("payment_status") == "SUCCESS"), None)
        if successful:
            await self.process_webhook(
                __import__("json").dumps({"data": {"order": {"order_id": order.provider_order_id}, "payment": successful}}).encode(),
                "server-verification",
                base64.b64encode(hmac.new((self.settings.CASHFREE_WEBHOOK_SECRET or self.settings.CASHFREE_SECRET_KEY).encode(), b"server-verification" + __import__("json").dumps({"data": {"order": {"order_id": order.provider_order_id}, "payment": successful}}).encode(), hashlib.sha256).digest()).decode(),
            )
        return PaymentStatusDTO(order_id=order.id, payment_status=order.payment_status, order_status=order.status, fulfillment_status=order.fulfillment_status, provider_reference=order.provider_reference)