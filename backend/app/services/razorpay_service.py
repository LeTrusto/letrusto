"""Razorpay order creation and server-side payment verification."""

import json
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from uuid import UUID

import razorpay
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.entities import Order, PaymentAttempt, RefundRequest, User
from app.schemas.payments import PaymentStatusDTO, RazorpayOrderDTO, RazorpayPaymentVerification
from app.services.fulfillment_service import FulfillmentService
from app.services.inventory_reservation_service import InventoryReservationService


class RazorpayService:
    provider = "RAZORPAY"

    def __init__(self, db: Session, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings or get_settings()

    @property
    def configured(self) -> bool:
        return bool(self.settings.RAZORPAY_KEY_ID and self.settings.RAZORPAY_KEY_SECRET)

    def _client(self):
        if not self.configured:
            raise BadRequestError("Razorpay credentials are not configured")
        return razorpay.Client(auth=(self.settings.RAZORPAY_KEY_ID, self.settings.RAZORPAY_KEY_SECRET))

    def _order(self, user: User, order_id: UUID, *, for_update: bool = False) -> Order:
        statement = select(Order).where(Order.id == order_id, Order.user_id == user.id)
        if for_update:
            statement = statement.with_for_update()
        order = self.db.scalar(statement)
        if order is None:
            raise NotFoundError("Order not found")
        return order

    @staticmethod
    def _amount_in_paise(order: Order) -> int:
        if order.currency != "INR":
            raise BadRequestError("Razorpay payments require INR")
        amount = (Decimal(order.total) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        if amount <= 0:
            raise BadRequestError("Order total must be positive")
        return int(amount)

    def create_order(self, user: User, order_id: UUID) -> RazorpayOrderDTO:
        order = self._order(user, order_id, for_update=True)
        if order.status != "PENDING_PAYMENT" or order.payment_status in {"PAID", "REFUNDED", "CANCELLED"}:
            raise BadRequestError("Order is not payable")
        if order.payment_provider and order.payment_provider != self.provider:
            raise BadRequestError("Order already has a different payment provider")

        amount = self._amount_in_paise(order)
        if order.provider_order_id and order.payment_provider == self.provider:
            return RazorpayOrderDTO(
                order_id=order.id,
                provider=self.provider,
                key_id=self.settings.RAZORPAY_KEY_ID,
                razorpay_order_id=order.provider_order_id,
                amount=amount,
                currency=order.currency,
            )

        client = self._client()
        try:
            provider_order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "receipt": order.order_number,
                "notes": {
                    "letrusto_order_id": str(order.id),
                    "letrusto_order_number": order.order_number,
                },
            })
        except Exception as exc:
            raise BadRequestError("Razorpay order could not be created") from exc

        provider_order_id = str(provider_order.get("id") or "")
        if not provider_order_id:
            raise BadRequestError("Razorpay returned no order ID")

        order.payment_provider = self.provider
        order.provider_order_id = provider_order_id
        attempt = self.db.scalar(select(PaymentAttempt).where(
            PaymentAttempt.order_id == order.id,
            PaymentAttempt.provider == self.provider,
            PaymentAttempt.provider_order_id == provider_order_id,
        ))
        if attempt is None:
            self.db.add(PaymentAttempt(
                order=order,
                provider=self.provider,
                provider_order_id=provider_order_id,
                status="PENDING",
            ))
        self.db.commit()
        return RazorpayOrderDTO(
            order_id=order.id,
            provider=self.provider,
            key_id=self.settings.RAZORPAY_KEY_ID,
            razorpay_order_id=provider_order_id,
            amount=amount,
            currency=order.currency,
        )

    async def verify_payment(
        self,
        user: User,
        order_id: UUID,
        payload: RazorpayPaymentVerification,
    ) -> PaymentStatusDTO:
        order = self._order(user, order_id, for_update=True)
        if order.payment_provider != self.provider or order.provider_order_id != payload.razorpay_order_id:
            raise BadRequestError("Razorpay order does not match the LeTrusto order")
        if order.payment_status == "PAID":
            attempt = self.db.scalar(select(PaymentAttempt).where(
                PaymentAttempt.order_id == order.id,
                PaymentAttempt.provider_payment_id == payload.razorpay_payment_id,
            ))
            if attempt is None:
                raise BadRequestError("Order has already been paid")
            return self._status(order)
        if order.status != "PENDING_PAYMENT" or order.payment_status in {"CANCELLED", "REFUNDED"}:
            raise BadRequestError("Order is not payable")

        client = self._client()
        try:
            provider_order = client.order.fetch(payload.razorpay_order_id)
            payment = client.payment.fetch(payload.razorpay_payment_id)
            client.utility.verify_payment_signature({
                "razorpay_order_id": payload.razorpay_order_id,
                "razorpay_payment_id": payload.razorpay_payment_id,
                "razorpay_signature": payload.razorpay_signature,
            })
        except Exception as exc:
            raise BadRequestError("Invalid Razorpay payment signature or payment details") from exc

        expected_amount = self._amount_in_paise(order)
        payment_status = str(payment.get("status") or "").lower()
        if (
            str(payment.get("order_id") or "") != payload.razorpay_order_id
            or int(payment.get("amount") or 0) != expected_amount
            or str(payment.get("currency") or "") != order.currency
            or int(provider_order.get("amount") or 0) != expected_amount
            or str(provider_order.get("currency") or "") != order.currency
            or payment_status != "captured"
        ):
            raise BadRequestError("Razorpay payment does not match the order")

        attempt = self.db.scalar(select(PaymentAttempt).where(
            PaymentAttempt.order_id == order.id,
            PaymentAttempt.provider == self.provider,
            PaymentAttempt.provider_order_id == payload.razorpay_order_id,
        ))
        if attempt is None:
            raise BadRequestError("Razorpay payment attempt not found")
        if attempt.provider_payment_id and attempt.provider_payment_id != payload.razorpay_payment_id:
            raise BadRequestError("Razorpay payment attempt does not match")

        return await self._mark_payment_success(order, attempt, payload.razorpay_payment_id)

    async def process_webhook(self, raw_body: bytes, signature: str | None) -> None:
        """Verify and process the minimum Razorpay payment/refund event set."""
        try:
            body_text = raw_body.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise BadRequestError("Invalid Razorpay webhook payload") from exc
        self.verify_webhook_signature(
            body_text,
            signature or "",
            self.settings.RAZORPAY_WEBHOOK_SECRET,
        )
        try:
            body = json.loads(body_text)
        except json.JSONDecodeError as exc:
            raise BadRequestError("Invalid Razorpay webhook payload") from exc

        event = body.get("event")
        entity = ((body.get("payload") or {}).get("payment") or {}).get("entity") or {}
        if event in {"payment.captured", "payment.failed"}:
            await self._process_payment_webhook(event, entity)
            return
        if event in {"refund.processed", "refund.failed"}:
            self._process_refund_webhook(event, body)

    async def _process_payment_webhook(self, event: str, payment: dict) -> None:
        provider_order_id = str(payment.get("order_id") or "")
        provider_payment_id = str(payment.get("id") or "")
        if not provider_order_id or not provider_payment_id:
            raise BadRequestError("Razorpay webhook has no payment relationship")
        order = self.db.scalar(
            select(Order).where(
                Order.payment_provider == self.provider,
                Order.provider_order_id == provider_order_id,
            ).with_for_update()
        )
        if order is None:
            raise NotFoundError("Razorpay order not found")
        attempt = self.db.scalar(select(PaymentAttempt).where(
            PaymentAttempt.order_id == order.id,
            PaymentAttempt.provider == self.provider,
            PaymentAttempt.provider_order_id == provider_order_id,
        ))
        if attempt is None:
            raise BadRequestError("Razorpay payment attempt not found")
        if attempt.provider_payment_id and attempt.provider_payment_id != provider_payment_id:
            raise BadRequestError("Razorpay payment attempt does not match")

        if event == "payment.failed":
            if order.payment_status == "PAID":
                return
            attempt.provider_payment_id = provider_payment_id
            attempt.status = "FAILED"
            attempt.failure_reason = str(payment.get("error_description") or "Razorpay payment failed")[:500]
            order.payment_status = "FAILED"
            order.payment_failure_reason = attempt.failure_reason
            if order.status == "PENDING_PAYMENT":
                InventoryReservationService(self.db).release_for_order(order.id)
            self.db.commit()
            return

        if order.payment_status == "PAID":
            if attempt.provider_payment_id == provider_payment_id:
                return
            raise BadRequestError("Order has already been paid")
        if order.status != "PENDING_PAYMENT":
            raise BadRequestError("Order is not payable")
        if (
            int(payment.get("amount") or 0) != self._amount_in_paise(order)
            or str(payment.get("currency") or "") != order.currency
            or str(payment.get("status") or "").lower() != "captured"
        ):
            raise BadRequestError("Razorpay payment does not match the order")
        await self._mark_payment_success(order, attempt, provider_payment_id)

    def _process_refund_webhook(self, event: str, body: dict) -> None:
        refund_entity = ((body.get("payload") or {}).get("refund") or {}).get("entity") or {}
        provider_refund_id = str(refund_entity.get("id") or "")
        provider_payment_id = str(refund_entity.get("payment_id") or "")
        if not provider_refund_id:
            raise BadRequestError("Razorpay webhook has no refund ID")
        refund = self.db.scalar(select(RefundRequest).where(
            RefundRequest.provider == self.provider,
            RefundRequest.provider_refund_id == provider_refund_id,
        ))
        if refund is None and provider_payment_id:
            attempt = self.db.scalar(select(PaymentAttempt).where(
                PaymentAttempt.provider == self.provider,
                PaymentAttempt.provider_payment_id == provider_payment_id,
            ))
            if attempt:
                refund = self.db.scalar(select(RefundRequest).where(
                    RefundRequest.order_id == attempt.order_id,
                    RefundRequest.provider == self.provider,
                ))
        if refund is None:
            return
        if refund.status in {"SUCCESS", "FAILED"}:
            return
        refund.provider_refund_id = provider_refund_id
        if event == "refund.processed":
            refund.status = "SUCCESS"
            refund.completed_at = datetime.now(timezone.utc)
            refund.order.payment_status = "REFUNDED"
            refund.order.status = "REFUNDED"
        else:
            refund.status = "FAILED"
            refund.failed_at = datetime.now(timezone.utc)
            refund.failure_reason = str(refund_entity.get("failure_reason") or "Razorpay refund failed")[:500]
            refund.order.payment_status = "REFUND_FAILED"
        self.db.commit()

    async def _mark_payment_success(
        self,
        order: Order,
        attempt: PaymentAttempt,
        provider_payment_id: str,
    ) -> PaymentStatusDTO:
        if order.payment_status == "PAID":
            return self._status(order)
        attempt.provider_payment_id = provider_payment_id
        attempt.status = "CAPTURED"
        order.provider_reference = provider_payment_id
        order.payment_status = "PAID"
        order.status = "PAID"
        order.paid_at = order.paid_at or datetime.now(timezone.utc)
        reservation_safe = InventoryReservationService(self.db).consume_for_order(order.id)
        if not reservation_safe:
            order.fulfillment_status = "FAILED"
            order.fulfillment_failure_reason = "Inventory reservation expired before payment confirmation"
        self.db.commit()
        if reservation_safe:
            await FulfillmentService(self.db).submit(order.id)
        return self._status(order)

    @staticmethod
    def verify_payment_signature(payload: dict[str, str], key_secret: str) -> None:
        if not key_secret:
            raise BadRequestError("Razorpay credentials are not configured")
        try:
            razorpay.Client(auth=("", key_secret)).utility.verify_payment_signature(payload)
        except Exception as exc:
            raise BadRequestError("Invalid Razorpay payment signature") from exc

    @staticmethod
    def verify_webhook_signature(raw_body: str, signature: str | None, webhook_secret: str) -> None:
        if not signature:
            raise BadRequestError("Razorpay webhook signature is missing")
        if not webhook_secret:
            raise BadRequestError("Razorpay webhook secret is not configured")
        try:
            razorpay.Utility().verify_webhook_signature(raw_body, signature, webhook_secret)
        except Exception as exc:
            raise BadRequestError("Invalid Razorpay webhook signature") from exc

    @staticmethod
    def _status(order: Order) -> PaymentStatusDTO:
        return PaymentStatusDTO(
            order_id=order.id,
            payment_status=order.payment_status,
            order_status=order.status,
            fulfillment_status=order.fulfillment_status,
            provider_reference=order.provider_reference,
        )