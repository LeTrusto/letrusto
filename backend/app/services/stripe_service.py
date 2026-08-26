"""Stripe-hosted Checkout creation and webhook processing."""

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

import stripe
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.entities import Order, PaymentAttempt, User
from app.schemas.payments import PaymentStatusDTO, StripeCheckoutSessionDTO
from app.services.fulfillment_service import FulfillmentService
from app.services.inventory_reservation_service import InventoryReservationService


class StripeService:
    provider = "STRIPE"

    def __init__(self, db: Session, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings or get_settings()

    @property
    def configured(self) -> bool:
        return bool(self.settings.STRIPE_SECRET_KEY)

    @staticmethod
    def _amount_in_minor_units(order: Order) -> int:
        amount = (Decimal(order.total) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        if amount <= 0:
            raise BadRequestError("Order total must be positive")
        return int(amount)

    def _order(self, user: User, order_id: UUID, *, for_update: bool = False) -> Order:
        statement = select(Order).where(Order.id == order_id, Order.user_id == user.id)
        if for_update:
            statement = statement.with_for_update()
        order = self.db.scalar(statement)
        if order is None:
            raise NotFoundError("Order not found")
        return order

    def create_session(self, user: User, order_id: UUID) -> StripeCheckoutSessionDTO:
        order = self._order(user, order_id, for_update=True)
        if order.status != "PENDING_PAYMENT" or order.payment_status in {"PAID", "REFUNDED", "CANCELLED"}:
            raise BadRequestError("Order is not payable")
        if order.payment_provider and order.payment_provider != self.provider:
            raise BadRequestError("Order already has a different payment provider")
        if not self.configured:
            raise BadRequestError("Stripe credentials are not configured")

        if order.payment_session_id and order.payment_provider == self.provider:
            stripe.api_key = self.settings.STRIPE_SECRET_KEY
            try:
                session = stripe.checkout.Session.retrieve(order.payment_session_id)
            except stripe.StripeError as exc:
                raise BadRequestError("Stripe payment session could not be retrieved") from exc
            if session.url:
                return self._dto(order, session.id, session.url)

        stripe.api_key = self.settings.STRIPE_SECRET_KEY
        try:
            session = stripe.checkout.Session.create(
                mode="payment",
                customer_email=order.customer_email,
                client_reference_id=str(order.id),
                line_items=[
                    {
                        "price_data": {
                            "currency": order.currency.lower(),
                            "unit_amount": int((Decimal(item.unit_price) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
                            "product_data": {"name": item.product_name},
                        },
                        "quantity": item.quantity,
                    }
                    for item in order.items
                ],
                metadata={"letrusto_order_id": str(order.id), "letrusto_order_number": order.order_number},
                success_url=self.settings.STRIPE_SUCCESS_URL.format(order_id=order.id),
                cancel_url=self.settings.STRIPE_CANCEL_URL,
            )
        except stripe.StripeError as exc:
            raise BadRequestError("Stripe payment session could not be created") from exc
        if not session.id or not session.url:
            raise BadRequestError("Stripe returned no checkout URL")

        order.payment_provider = self.provider
        order.provider_order_id = session.id
        order.payment_session_id = session.id
        order.payment_attempted_at = datetime.now(timezone.utc)
        self.db.add(PaymentAttempt(order=order, provider=self.provider, provider_order_id=session.id, session_id=session.id, status="PENDING"))
        self.db.commit()
        return self._dto(order, session.id, session.url)

    def _dto(self, order: Order, session_id: str, checkout_url: str) -> StripeCheckoutSessionDTO:
        return StripeCheckoutSessionDTO(order_id=order.id, provider=self.provider, provider_order_id=session_id, checkout_url=checkout_url, amount=order.total, currency=order.currency)

    async def process_webhook(self, raw_body: bytes, signature: str | None) -> None:
        if not signature or not self.settings.STRIPE_WEBHOOK_SECRET:
            raise BadRequestError("Stripe webhook signature is missing or not configured")
        try:
            event = stripe.Webhook.construct_event(raw_body, signature, self.settings.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.SignatureVerificationError) as exc:
            raise BadRequestError("Invalid Stripe webhook signature or payload") from exc

        if event.type not in {"checkout.session.completed", "checkout.session.async_payment_succeeded", "checkout.session.async_payment_failed", "checkout.session.expired"}:
            return
        session = event.data.object
        order_id = ((session.get("metadata") or {}).get("letrusto_order_id") or session.get("client_reference_id"))
        if not order_id:
            raise BadRequestError("Stripe webhook has no LeTrusto order ID")
        order = self.db.scalar(select(Order).where(Order.id == UUID(str(order_id))).with_for_update())
        if order is None:
            raise NotFoundError("Stripe order not found")
        attempt = self.db.scalar(select(PaymentAttempt).where(PaymentAttempt.order_id == order.id, PaymentAttempt.provider == self.provider, PaymentAttempt.provider_order_id == str(session.id)))
        if attempt is None:
            attempt = PaymentAttempt(order=order, provider=self.provider, provider_order_id=str(session.id), session_id=str(session.id), status="PENDING")
            self.db.add(attempt)
        payment_intent = session.get("payment_intent")
        if payment_intent:
            attempt.provider_payment_id = str(payment_intent)
        if event.type in {"checkout.session.completed", "checkout.session.async_payment_succeeded"} and session.get("payment_status") == "paid":
            if order.payment_status != "PAID":
                order.payment_status = "PAID"
                order.status = "PAID"
                order.paid_at = order.paid_at or datetime.now(timezone.utc)
                order.provider_reference = attempt.provider_payment_id or str(session.id)
                attempt.status = "CAPTURED"
                reservation_safe = InventoryReservationService(self.db).consume_for_order(order.id)
                if not reservation_safe:
                    order.fulfillment_status = "FAILED"
                    order.fulfillment_failure_reason = "Inventory reservation expired before payment confirmation"
                self.db.commit()
                if reservation_safe:
                    await FulfillmentService(self.db).submit(order.id)
                return
        elif event.type in {"checkout.session.async_payment_failed", "checkout.session.expired"}:
            if order.payment_status != "PAID":
                order.payment_status = "FAILED"
                order.payment_failure_reason = "Stripe payment failed or checkout expired"
                attempt.status = "FAILED"
                InventoryReservationService(self.db).release_for_order(order.id)
        self.db.commit()

    @staticmethod
    def _status(order: Order) -> PaymentStatusDTO:
        return PaymentStatusDTO(order_id=order.id, payment_status=order.payment_status, order_status=order.status, fulfillment_status=order.fulfillment_status, provider_reference=order.provider_reference)