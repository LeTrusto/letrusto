"""Comprehensive tests for order cancellation and refund lifecycle."""

import asyncio
import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch, MagicMock
from uuid import uuid4

import pytest

from app.core.exceptions import BadRequestError, NotFoundError
from app.db.session import SessionLocal
from app.models.entities import Order, PaymentAttempt, Product, ProductVariant, RefundRequest, User
from app.services.cancellation_service import CancellationService, is_fulfillable
from app.services.cashfree_service import CashfreeService


def _fake_settings():
    """Return a mock settings object with fake Cashfree credentials for testing."""
    from app.core.config import get_settings
    s = get_settings()
    # Create a copy-like object that has credentials set
    class FakeSettings:
        pass
    fake = FakeSettings()
    for attr in dir(s):
        if not attr.startswith("_"):
            try:
                setattr(fake, attr, getattr(s, attr))
            except Exception:
                pass
    fake.CASHFREE_APP_ID = "test_app_id"
    fake.CASHFREE_SECRET_KEY = "test_secret_key"
    fake.CASHFREE_WEBHOOK_SECRET = "webhook-secret"
    fake.CASHFREE_ENV = "sandbox"
    fake.CASHFREE_API_VERSION = "2026-01-01"
    return fake


def _fixture(db):
    """Create isolated test data that doesn't touch live products."""
    suffix = uuid4().hex[:8]
    user = User(email=f"cancel-{suffix}@test.local", full_name="Cancel Test", role="user")
    admin = User(email=f"admin-cancel-{suffix}@test.local", full_name="Admin Cancel", role="admin")
    product = Product(
        slug=f"cancel-test-{suffix}", name="Cancel Test Product", description="test",
        status="ACTIVE", supplier="cj", supplier_product_id=f"CJ-{suffix}",
        price_value=Decimal("250.00"), selling_price=Decimal("250.00"),
        ai_score=1, rating=Decimal("1.0"), ai_summary="", review_summary="",
    )
    variant = ProductVariant(
        product=product, supplier_variant_id=f"VID-{suffix}", supplier_variant_sku=f"SKU-{suffix}",
        name="Default", position=1, selling_price=Decimal("250.00"), cj_inventory=10, factory_inventory=100, active=True,
    )
    db.add_all([user, admin, product])
    db.commit()
    return user, admin, product, variant


def _make_order(db, user, *, status="PENDING_PAYMENT", payment_status="PENDING", fulfillment_status="PENDING",
                supplier_order_id=None, total=Decimal("500.00"), provider_order_id=None, payment_provider=None):
    order = Order(
        order_number=f"LT-TEST-{uuid4().hex[:8]}", user_id=user.id, status=status,
        payment_status=payment_status, fulfillment_status=fulfillment_status,
        subtotal=total, total=total, currency="INR",
        customer_name="Test", customer_email="test@test.local", customer_phone="9876543210",
        shipping_address={"address": "1 Test St", "city": "Bengaluru", "state": "Karnataka", "postal_code": "560001", "country": "IN"},
        idempotency_key=f"key-{uuid4().hex[:8]}",
        supplier_order_id=supplier_order_id, provider_order_id=provider_order_id, payment_provider=payment_provider,
    )
    db.add(order)
    db.commit()
    return order


def _make_paid_order(db, user, **kwargs):
    payment_provider = kwargs.pop("payment_provider", "CASHFREE")
    order = _make_order(db, user, status="PAID", payment_status="PAID", payment_provider=payment_provider, provider_order_id=f"cf-{uuid4().hex[:8]}", **kwargs)
    attempt = PaymentAttempt(order=order, provider="CASHFREE", provider_order_id=order.provider_order_id, status="SUCCESS", provider_payment_id=f"cf-pay-{uuid4().hex[:6]}")
    db.add(attempt)
    db.commit()
    return order


def _cleanup(db, *entities):
    for e in entities:
        db.delete(e)
    db.commit()
    db.close()


# ── Customer Cancellation Tests ──────────────────────────────


class TestCustomerCancellation:
    def test_cancel_unpaid_order(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_order(db, user)
        try:
            svc = CancellationService(db)
            result = svc.cancel_by_customer(user, order.id)
            assert result.status == "CANCELLED"
            assert result.payment_status == "CANCELLED"
            assert result.cancelled_by == "customer"
            assert result.cancelled_at is not None
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)

    @patch("app.services.cashfree_service.httpx.post")
    def test_cancel_paid_unfulfilled_order_initiates_refund(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"cf_refund_id": "rfnd_test_123", "refund_status": "PENDING"})
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user)
        try:
            svc = CancellationService(db, settings=_fake_settings())
            result = svc.cancel_by_customer(user, order.id)
            assert result.status == "CANCELLED"
            assert result.payment_status == "REFUND_PENDING"
            refund = svc.get_refund_status(order.id)
            assert refund is not None
            assert refund.amount == order.total
            assert refund.status == "PROCESSING"
            assert refund.provider_refund_id == "rfnd_test_123"
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)

    def test_cancel_rejected_after_cj_submission(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user, supplier_order_id=f"CJ-12345-{uuid4().hex[:8]}")
        try:
            svc = CancellationService(db)
            with pytest.raises(BadRequestError, match="submitted to supplier"):
                svc.cancel_by_customer(user, order.id)
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)

    def test_cancel_rejected_after_shipped(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user)
        order.fulfillment_status = "SHIPPED"
        db.commit()
        try:
            svc = CancellationService(db)
            with pytest.raises(BadRequestError, match="progressed"):
                svc.cancel_by_customer(user, order.id)
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)

    def test_cancel_rejected_for_other_user(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_order(db, user)
        other = User(email=f"other-{uuid4().hex[:6]}@test.local", full_name="Other")
        db.add(other)
        db.commit()
        try:
            svc = CancellationService(db)
            with pytest.raises(NotFoundError):
                svc.cancel_by_customer(other, order.id)
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            db.delete(other)
            _cleanup(db, user, admin, product)

    @patch("app.services.cashfree_service.httpx.post")
    def test_repeated_cancellation_is_idempotent(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"cf_refund_id": "rfnd_idem", "refund_status": "PENDING"})
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user)
        try:
            svc = CancellationService(db, settings=_fake_settings())
            svc.cancel_by_customer(user, order.id)
            # Second call should not create duplicate refund
            result = svc.cancel_by_customer(user, order.id)
            assert result.status == "CANCELLED"
            refunds = db.query(RefundRequest).filter(RefundRequest.order_id == order.id).all()
            assert len(refunds) == 1
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)


# ── Admin Cancellation Tests ─────────────────────────────────


class TestAdminCancellation:
    @patch("app.services.cashfree_service.httpx.post")
    def test_admin_cancel_paid_order(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"cf_refund_id": "rfnd_admin", "refund_status": "SUCCESS"})
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user)
        try:
            svc = CancellationService(db, settings=_fake_settings())
            result = svc.cancel_by_admin(admin, order.id, "Test admin cancel")
            assert result.status in {"CANCELLED", "REFUNDED"}
            assert "admin:" in result.cancelled_by
            refund = svc.get_refund_status(order.id)
            assert refund.requested_by == "admin"
            assert refund.admin_id == admin.id
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)


# ── Refund Provider Tests ────────────────────────────────────


class TestRefundProvider:
    def test_razorpay_order_uses_razorpay_refund(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user, payment_provider="RAZORPAY")
        order.provider_order_id = f"order_{uuid4().hex[:8]}"
        attempt = PaymentAttempt(order=order, provider="RAZORPAY", provider_order_id=order.provider_order_id, status="CAPTURED", provider_payment_id=f"pay_razorpay_{uuid4().hex[:8]}")
        db.add(attempt)
        db.commit()
        cashfree = MagicMock()
        razorpay = MagicMock()
        razorpay.request_refund.return_value = {"provider_refund_id": "rfnd_razorpay", "provider_status": "pending"}
        try:
            result = CancellationService(db, cashfree_service=cashfree, razorpay_service=razorpay).cancel_by_customer(user, order.id)
            assert result.payment_status == "REFUND_PENDING"
            refund = db.query(RefundRequest).filter(RefundRequest.order_id == order.id).one()
            assert refund.provider == "RAZORPAY"
            razorpay.request_refund.assert_called_once()
            cashfree.request_refund.assert_not_called()
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)

    def test_unsupported_provider_fails_without_refund_mutation(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user, payment_provider="UNKNOWN")
        try:
            with pytest.raises(BadRequestError, match="missing or unsupported"):
                CancellationService(db).cancel_by_customer(user, order.id)
            db.refresh(order)
            assert order.status == "PAID"
            assert db.query(RefundRequest).filter(RefundRequest.order_id == order.id).count() == 0
        finally:
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)

    def test_razorpay_refund_failure_is_retryable(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user, payment_provider="RAZORPAY")
        order.provider_order_id = f"order_{uuid4().hex[:8]}"
        db.add(PaymentAttempt(order=order, provider="RAZORPAY", provider_order_id=order.provider_order_id, status="CAPTURED", provider_payment_id=f"pay_razorpay_fail_{uuid4().hex[:8]}"))
        db.commit()
        razorpay = MagicMock()
        razorpay.request_refund.return_value = {"provider_status": "failed", "failure_reason": "Provider rejected refund"}
        try:
            result = CancellationService(db, razorpay_service=razorpay).cancel_by_customer(user, order.id)
            refund = db.query(RefundRequest).filter(RefundRequest.order_id == order.id).one()
            assert result.payment_status == "REFUND_FAILED"
            assert refund.status == "FAILED"
            assert refund.failure_reason == "Provider rejected refund"
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)

    @patch("app.services.cashfree_service.httpx.post")
    def test_refund_amount_from_server_not_browser(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"cf_refund_id": "rfnd_amt", "refund_status": "PENDING"})
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user, total=Decimal("799.00"))
        try:
            svc = CancellationService(db, settings=_fake_settings())
            svc.cancel_by_customer(user, order.id)
            refund = svc.get_refund_status(order.id)
            assert refund.amount == Decimal("799.00")
            call_payload = mock_post.call_args[1]["json"]
            assert call_payload["refund_amount"] == 799.0
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)

    @patch("app.services.cashfree_service.httpx.post")
    def test_refund_provider_failure(self, mock_post):
        mock_post.return_value = MagicMock(status_code=400, json=lambda: {"message": "Invalid order"})
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user)
        try:
            svc = CancellationService(db, settings=_fake_settings())
            svc.cancel_by_customer(user, order.id)
            refund = svc.get_refund_status(order.id)
            assert refund.status == "FAILED"
            assert refund.failure_reason == "Invalid order"
            repeated = svc.cancel_by_customer(user, order.id)
            assert repeated.payment_status == "REFUND_FAILED"
            assert db.query(RefundRequest).filter(RefundRequest.order_id == order.id).count() == 1
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)

    @patch("app.services.cashfree_service.httpx.post")
    def test_refund_retry(self, mock_post):
        mock_post.side_effect = [
            MagicMock(status_code=500, json=lambda: {}),
            MagicMock(status_code=200, json=lambda: {"cf_refund_id": "rfnd_retry", "refund_status": "PENDING"}),
        ]
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user)
        try:
            svc = CancellationService(db, settings=_fake_settings())
            svc.cancel_by_customer(user, order.id)
            refund = svc.get_refund_status(order.id)
            assert refund.status == "FAILED"

            mock_post.side_effect = [MagicMock(status_code=200, json=lambda: {"cf_refund_id": "rfnd_retry2", "refund_status": "PENDING"})]
            retried = svc.retry_failed_refund(admin, order.id)
            assert retried.status == "PROCESSING"
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)

    @patch("app.services.cashfree_service.httpx.post")
    def test_duplicate_refund_request_rejected(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"cf_refund_id": "rfnd_dup", "refund_status": "PENDING"})
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user)
        try:
            svc = CancellationService(db, settings=_fake_settings())
            svc.cancel_by_customer(user, order.id)
            # Calling initiate again returns existing
            existing = svc._existing_refund(order)
            assert existing is not None
            count = db.query(RefundRequest).filter(RefundRequest.order_id == order.id).count()
            assert count == 1
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)

    def test_refund_webhook_success(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user)
        refund_id = f"rfnd_wh_{uuid4().hex[:8]}"
        refund = RefundRequest(
            order=order, provider="CASHFREE", provider_order_id=order.provider_order_id or "",
            amount=order.total, currency="INR", status="PROCESSING",
            idempotency_key=f"refund-{order.id}", provider_refund_id=refund_id,
            requested_by="customer",
        )
        db.add(refund)
        order.payment_status = "REFUND_PENDING"
        order.status = "CANCELLED"
        db.commit()
        try:
            svc = CancellationService(db)
            svc.process_refund_webhook(refund_id, "SUCCESS", str(order.id))
            db.refresh(refund)
            db.refresh(order)
            assert refund.status == "SUCCESS"
            assert refund.completed_at is not None
            assert order.payment_status == "REFUNDED"
            assert order.status == "REFUNDED"
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)

    def test_refund_webhook_duplicate_is_idempotent(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user)
        refund_id = f"rfnd_duplicate_{uuid4().hex[:8]}"
        refund = RefundRequest(
            order=order, provider="CASHFREE", provider_order_id=order.provider_order_id or "",
            amount=order.total, currency="INR", status="SUCCESS",
            idempotency_key=f"refund-{order.id}", provider_refund_id=refund_id,
            requested_by="customer", completed_at=datetime.now(timezone.utc),
        )
        db.add(refund)
        order.payment_status = "REFUNDED"
        order.status = "REFUNDED"
        db.commit()
        try:
            svc = CancellationService(db)
            svc.process_refund_webhook(refund_id, "SUCCESS", str(order.id))
            # No error, no state change
            db.refresh(refund)
            assert refund.status == "SUCCESS"
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)

    def test_signed_cashfree_refund_webhook_updates_refund(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user)
        refund_id = f"rfnd_signed_{uuid4().hex[:8]}"
        refund = RefundRequest(
            order=order,
            provider="CASHFREE",
            provider_order_id=order.provider_order_id or "",
            amount=order.total,
            currency="INR",
            status="PROCESSING",
            idempotency_key=f"refund-{order.id}",
            provider_refund_id=refund_id,
            requested_by="customer",
        )
        db.add(refund)
        order.payment_status = "REFUND_PENDING"
        order.status = "CANCELLED"
        db.commit()
        try:
            body = json.dumps(
                {
                    "type": "REFUND_STATUS_WEBHOOK",
                    "data": {
                        "refund": {
                            "cf_refund_id": refund_id,
                            "order_id": order.provider_order_id,
                            "refund_status": "SUCCESS",
                        }
                    },
                }
            ).encode()
            timestamp = "refund-webhook-test"
            secret = "webhook-secret"
            signature = base64.b64encode(
                hmac.new(secret.encode(), timestamp.encode() + body, hashlib.sha256).digest()
            ).decode()
            service = CashfreeService(db, _fake_settings())
            asyncio.run(service.process_webhook(body, timestamp, signature))
            db.refresh(refund)
            db.refresh(order)
            assert refund.status == "SUCCESS"
            assert order.payment_status == "REFUNDED"
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)


# ── Fulfillment Safety Tests ─────────────────────────────────


class TestFulfillmentSafety:
    def test_unpaid_order_not_fulfillable(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_order(db, user)
        try:
            assert not is_fulfillable(order)
        finally:
            db.delete(order)
            _cleanup(db, user, admin, product)

    def test_cancelled_order_not_fulfillable(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_order(db, user, status="CANCELLED", payment_status="CANCELLED")
        order.cancelled_at = datetime.now(timezone.utc)
        db.commit()
        try:
            assert not is_fulfillable(order)
        finally:
            db.delete(order)
            _cleanup(db, user, admin, product)

    def test_refund_pending_not_fulfillable(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_order(db, user, status="CANCELLED", payment_status="REFUND_PENDING")
        try:
            assert not is_fulfillable(order)
        finally:
            db.delete(order)
            _cleanup(db, user, admin, product)

    def test_refunded_order_not_fulfillable(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_order(db, user, status="REFUNDED", payment_status="REFUNDED")
        try:
            assert not is_fulfillable(order)
        finally:
            db.delete(order)
            _cleanup(db, user, admin, product)

    def test_paid_order_is_fulfillable(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_order(db, user, status="PAID", payment_status="PAID")
        try:
            assert is_fulfillable(order)
        finally:
            db.delete(order)
            _cleanup(db, user, admin, product)

    @patch("app.services.cashfree_service.httpx.post")
    def test_cancel_then_fulfillment_blocked(self, mock_post):
        """Race condition: cancel wins, fulfillment must be blocked."""
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"cf_refund_id": "rfnd_race", "refund_status": "PENDING"})
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user)
        try:
            svc = CancellationService(db, settings=_fake_settings())
            svc.cancel_by_customer(user, order.id)
            db.refresh(order)
            assert not is_fulfillable(order)
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.delete(order)
            _cleanup(db, user, admin, product)


# ── Idempotency Constraint Test ──────────────────────────────


class TestIdempotencyConstraint:
    def test_unique_idempotency_key_enforced(self):
        db = SessionLocal()
        user, admin, product, _ = _fixture(db)
        order = _make_paid_order(db, user)
        try:
            r1 = RefundRequest(
                order=order, provider="CASHFREE", provider_order_id="cf-test",
                amount=Decimal("100"), currency="INR", status="PENDING",
                idempotency_key="unique-key-test", requested_by="customer",
            )
            db.add(r1)
            db.commit()

            r2 = RefundRequest(
                order=order, provider="CASHFREE", provider_order_id="cf-test",
                amount=Decimal("100"), currency="INR", status="PENDING",
                idempotency_key="unique-key-test", requested_by="customer",
            )
            db.add(r2)
            with pytest.raises(Exception):
                db.commit()
            db.rollback()
        finally:
            db.query(RefundRequest).filter(RefundRequest.order_id == order.id).delete()
            db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).delete()
            db.commit()
            db.delete(order)
            _cleanup(db, user, admin, product)
