from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.entities import OperationalAlertState, Product, ProductVariant
from app.services.email_service import EmailService


logger = logging.getLogger(__name__)


class OperationalAlertService:
    def __init__(self, db: Session, *, email_service: EmailService | None = None) -> None:
        settings = get_settings()
        self.db = db
        self.email_service = email_service or EmailService.from_settings(settings)
        self.recipient = settings.SUPPORT_EMAIL
        self.from_email = settings.FROM_EMAIL
        self.threshold = settings.LOW_STOCK_THRESHOLD
        self.cooldown = timedelta(minutes=settings.ALERT_EMAIL_COOLDOWN_MINUTES)

    def evaluate_low_stock(self, now: datetime | None = None) -> dict[str, int]:
        now = now or datetime.now(timezone.utc)
        variants = list(self.db.scalars(
            select(ProductVariant).join(Product).where(Product.status == "ACTIVE", Product.supplier == "cj", ProductVariant.active.is_(True))
        ).all())
        sent = suppressed = recovered = delivery_failures = 0
        current_keys: set[str] = set()
        for variant in variants:
            key = str(variant.id)
            current_keys.add(key)
            stock = max(0, variant.cj_inventory or 0)
            state = self._state("LOW_STOCK", key)
            if stock <= self.threshold:
                if state is None:
                    state = OperationalAlertState(alert_type="LOW_STOCK", alert_key=key)
                    self.db.add(state)
                    self.db.flush()
                if state.is_active and not (
                    state.delivery_failed_at
                    and state.last_alert_at
                    and now - state.last_alert_at >= self.cooldown
                ):
                    suppressed += 1
                    continue
                state.is_active = True
                state.recovered_at = None
                state.last_alert_at = now
                try:
                    self.email_service.send_template(
                        "operational_alert",
                        to=self.recipient,
                        from_email=self.from_email,
                        context={
                            "subject": "[LeTrusto Alert] Low inventory detected",
                            "details": [
                                ("Product", variant.product.name),
                                ("Variant / SKU", variant.supplier_variant_sku or variant.name or str(variant.id)),
                                ("Current sellable stock", str(stock)),
                                ("Alert threshold", str(self.threshold)),
                                ("Supplier", "cj"),
                                ("Detected at", now.isoformat()),
                            ],
                        },
                    )
                    state.delivery_failed_at = None
                    state.delivery_failure_reason = None
                    sent += 1
                except Exception as exc:
                    delivery_failures += 1
                    self._record_delivery_failure(state, exc, now)
                    logger.warning("Operational alert delivery failed", extra={"alert_type": "LOW_STOCK", "error_category": type(exc).__name__})
            elif state is not None and state.is_active:
                state.is_active = False
                state.recovered_at = now
                recovered += 1
        self.db.commit()
        return {"sent": sent, "suppressed": suppressed, "recovered": recovered, "delivery_failures": delivery_failures}

    def process_inventory_sync_failures(self, failures: list[dict[str, str]], now: datetime | None = None) -> dict[str, int]:
        now = now or datetime.now(timezone.utc)
        state = self._state("INVENTORY_SYNC_FAILURE", "cj")
        if not failures:
            if state is not None and state.is_active:
                state.is_active = False
                state.recovered_at = now
                self.db.commit()
                return {"sent": 0, "suppressed": 0, "recovered": 1, "delivery_failures": 0}
            return {"sent": 0, "suppressed": 0, "recovered": 0, "delivery_failures": 0}

        categories = sorted({item.get("category", "UnknownError") for item in failures})
        fingerprint = ",".join(categories)
        if state is not None and state.is_active and state.fingerprint == fingerprint and state.last_alert_at and now - state.last_alert_at < self.cooldown:
            return {"sent": 0, "suppressed": 1, "recovered": 0, "delivery_failures": 0}
        if state is None:
            state = OperationalAlertState(alert_type="INVENTORY_SYNC_FAILURE", alert_key="cj")
            self.db.add(state)
        state.is_active = True
        state.fingerprint = fingerprint
        state.recovered_at = None
        state.last_alert_at = now
        delivery_failures = 0
        try:
            self.email_service.send_template(
                "operational_alert",
                to=self.recipient,
                from_email=self.from_email,
                context={
                    "subject": "[LeTrusto Alert] Inventory synchronization failed",
                    "details": [
                        ("Supplier", "cj"),
                        ("Failed products", str(len(failures))),
                        ("Failure categories", fingerprint),
                        ("Detected at", now.isoformat()),
                    ],
                },
            )
            sent = 1
        except Exception as exc:
            sent = 0
            delivery_failures = 1
            self._record_delivery_failure(state, exc, now)
            logger.warning("Operational alert delivery failed", extra={"alert_type": "INVENTORY_SYNC_FAILURE", "error_category": type(exc).__name__})
        self.db.commit()
        return {"sent": sent, "suppressed": 0, "recovered": 0, "delivery_failures": delivery_failures}

    def _state(self, alert_type: str, alert_key: str) -> OperationalAlertState | None:
        return self.db.scalar(select(OperationalAlertState).where(
            OperationalAlertState.alert_type == alert_type,
            OperationalAlertState.alert_key == alert_key,
        ).with_for_update())

    @staticmethod
    def _record_delivery_failure(state: OperationalAlertState, exc: Exception, now: datetime) -> None:
        state.delivery_failed_at = now
        state.delivery_failure_reason = type(exc).__name__