"""Razorpay recurring subscription orchestration for SaaS plans."""

import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

import razorpay
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import BadRequestError
from app.models.entities import Subscription, User
from app.schemas.subscriptions import SubscriptionCreateResponse


logger = logging.getLogger(__name__)


class SubscriptionService:
    PLAN_NAMES = {"starter", "pro"}

    def __init__(self, db: Session, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings or get_settings()

    def _client(self) -> razorpay.Client:
        if not self.settings.RAZORPAY_KEY_ID or not self.settings.RAZORPAY_KEY_SECRET:
            raise BadRequestError("Razorpay credentials are not configured")
        return razorpay.Client(auth=(self.settings.RAZORPAY_KEY_ID, self.settings.RAZORPAY_KEY_SECRET))

    def _plan_id(self, plan_name: str) -> str:
        plan_id = {
            "starter": self.settings.RAZORPAY_STARTER_PLAN_ID,
            "pro": self.settings.RAZORPAY_PRO_PLAN_ID,
        }.get(plan_name)
        if not plan_id:
            raise BadRequestError(f"Razorpay plan is not configured for {plan_name}")
        return plan_id

    def create_subscription(self, user: User, plan_name: str) -> SubscriptionCreateResponse:
        if plan_name not in self.PLAN_NAMES:
            raise BadRequestError("Only starter and pro plans can be subscribed to")

        existing = self.db.scalar(
            select(Subscription)
            .where(
                Subscription.user_id == user.id,
                Subscription.plan_name == plan_name,
                Subscription.status.in_(["created", "authenticated", "active"]),
            )
            .order_by(Subscription.created_at.desc())
        )
        if existing and existing.razorpay_subscription_id:
            return SubscriptionCreateResponse(
                subscription_id=existing.razorpay_subscription_id,
                plan_name=existing.plan_name,
                key_id=self.settings.RAZORPAY_KEY_ID,
                status=existing.status,
            )

        try:
            plan_id = self._plan_id(plan_name)
            provider_subscription = self._client().subscription.create({
                "plan_id": plan_id,
                "total_count": 120,
                "customer_notify": 1,
                "notes": {
                    "letrusto_user_id": str(user.id),
                    "letrusto_plan_name": plan_name,
                },
            })
        except Exception as exc:
            if self.settings.APP_ENV == "development":
                logger.exception(
                    "Razorpay subscription creation failed: plan_name=%s plan_id=%s error_type=%s provider_error=%s",
                    plan_name,
                    locals().get("plan_id", "unresolved"),
                    type(exc).__name__,
                    _provider_error_summary(exc),
                )
            raise BadRequestError("Razorpay subscription could not be created") from exc

        provider_id = str(provider_subscription.get("id") or "")
        if not provider_id:
            raise BadRequestError("Razorpay returned no subscription ID")

        record = existing or Subscription(user_id=user.id, plan_name=plan_name)
        record.razorpay_subscription_id = provider_id
        record.status = str(provider_subscription.get("status") or "created")
        record.current_period_end = _epoch_to_datetime(provider_subscription.get("current_end"))
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return SubscriptionCreateResponse(
            subscription_id=provider_id,
            plan_name=plan_name,
            key_id=self.settings.RAZORPAY_KEY_ID,
            status=record.status,
        )

    def process_webhook(self, body: bytes, signature: str | None) -> None:
        if not self.settings.RAZORPAY_WEBHOOK_SECRET or not signature:
            raise BadRequestError("Invalid Razorpay subscription webhook")
        expected = hmac.new(
            self.settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise BadRequestError("Invalid Razorpay subscription webhook signature")

        try:
            payload = __import__("json").loads(body)
            event_name = str(payload.get("event") or "")
            entity: dict[str, Any] = payload["payload"]["subscription"]["entity"]
        except (ValueError, KeyError, TypeError) as exc:
            raise BadRequestError("Invalid Razorpay subscription webhook payload") from exc

        if event_name not in {"subscription.charged", "subscription.cancelled"}:
            return

        provider_id = str(entity.get("id") or "")
        if not provider_id:
            raise BadRequestError("Subscription webhook has no subscription ID")
        record = self.db.scalar(
            select(Subscription).where(Subscription.razorpay_subscription_id == provider_id)
        )
        if record is None:
            notes = entity.get("notes") or {}
            user_id = str(notes.get("letrusto_user_id") or "")
            if not user_id:
                raise BadRequestError("Subscription webhook cannot identify the user")
            record = self.db.scalar(select(Subscription).where(Subscription.user_id == user_id))
        if record is None:
            raise BadRequestError("Subscription record not found")

        record.razorpay_subscription_id = provider_id
        record.status = "active" if event_name == "subscription.charged" else "cancelled"
        record.current_period_end = _epoch_to_datetime(entity.get("current_end"))
        self.db.commit()


def _epoch_to_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return None


def _provider_error_summary(exc: Exception) -> str:
    raw_message = str(exc)
    try:
        payload = json.loads(raw_message)
    except (TypeError, ValueError):
        return raw_message[:500]

    if not isinstance(payload, dict):
        return raw_message[:500]
    error = payload.get("error")
    if isinstance(error, dict):
        summary = {
            key: error.get(key)
            for key in ("code", "description", "field", "source", "reason")
            if error.get(key) is not None
        }
        return json.dumps(summary, separators=(",", ":"))[:500]
    return json.dumps(payload, separators=(",", ":"))[:500]
