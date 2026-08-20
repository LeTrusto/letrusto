"""Focused tests for Razorpay order creation and payment verification."""

import asyncio
import hashlib
import hmac
import json
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.core.exceptions import BadRequestError, NotFoundError
from app.db.session import SessionLocal
from app.models.entities import Order, PaymentAttempt, RefundRequest, User
from app.services.razorpay_service import RazorpayService
from app.schemas.payments import RazorpayPaymentVerification


def settings(**overrides):
    values = dict(
        RAZORPAY_ENV="sandbox",
        RAZORPAY_KEY_ID="rzp_test_key",
        RAZORPAY_KEY_SECRET="test_secret",
        RAZORPAY_WEBHOOK_SECRET="webhook_secret",
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def make_order(db, *, status="PENDING_PAYMENT", payment_status="PENDING", total=Decimal("412.72")):
    suffix = uuid4().hex[:8]
    user = User(email=f"razorpay-{suffix}@example.com", full_name="Razorpay Test")
    order = Order(
        order_number=f"LT-RZ-{suffix}",
        user=user,
        status=status,
        payment_status=payment_status,
        fulfillment_status="PENDING",
        subtotal=total,
        total=total,
        currency="INR",
        customer_name="Buyer",
        customer_email="buyer@example.com",
        customer_phone="9876543210",
        shipping_address={"address": "1 Street", "city": "Bengaluru", "state": "Karnataka", "postal_code": "560001", "country": "IN"},
        idempotency_key=f"razorpay-{suffix}",
    )
    db.add(order)
    db.commit()
    return user, order


def cleanup(db, user, order, *, close=True):
    order_id = order.id
    user_id = user.id
    db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order_id).delete(synchronize_session=False)
    db.delete(order)
    db.delete(user)
    db.commit()
    if close:
        db.close()


def mock_client(monkeypatch, order_id, payment_id="pay_test"):
    client = MagicMock()
    client.order.create.return_value = {"id": "order_test_123"}
    client.order.fetch.return_value = {"id": order_id, "amount": 41272, "currency": "INR"}
    client.payment.fetch.return_value = {
        "id": payment_id,
        "order_id": order_id,
        "amount": 41272,
        "currency": "INR",
        "status": "captured",
    }
    client.utility.verify_payment_signature.return_value = None
    monkeypatch.setattr("app.services.razorpay_service.razorpay.Client", lambda auth: client)
    return client


def webhook_body(event, entity):
    return json.dumps({"event": event, "payload": {"payment": {"entity": entity}}}).encode()


def refund_webhook_body(event, entity):
    return json.dumps({"event": event, "payload": {"refund": {"entity": entity}}}).encode()


def webhook_signature(body, secret="webhook_secret"):
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def setup_webhook_order(db, *, payment_id="pay_webhook"):
    user, order = make_order(db)
    order.payment_provider = "RAZORPAY"
    order.provider_order_id = "order_webhook_123"
    attempt = PaymentAttempt(
        order=order,
        provider="RAZORPAY",
        provider_order_id="order_webhook_123",
        provider_payment_id=payment_id,
        status="PENDING",
    )
    db.add(attempt)
    db.commit()
    return user, order, attempt


def test_create_order_uses_server_total_and_paise(monkeypatch):
    db = SessionLocal(); user, order = make_order(db)
    try:
        client = mock_client(monkeypatch, "order_test_123")
        result = RazorpayService(db, settings()).create_order(user, order.id)
        payload = client.order.create.call_args.args[0]
        assert result.amount == 41272
        assert payload["amount"] == 41272
        assert payload["currency"] == "INR"
        assert payload["notes"]["letrusto_order_id"] == str(order.id)
        db.refresh(order)
        assert order.payment_provider == "RAZORPAY"
        assert order.provider_order_id == "order_test_123"
    finally:
        cleanup(db, user, order)


def test_create_order_has_no_frontend_amount_override_parameter():
    import inspect

    assert "amount" not in inspect.signature(RazorpayService.create_order).parameters


def test_missing_credentials_fail_safely():
    db = SessionLocal(); user, order = make_order(db)
    try:
        with pytest.raises(BadRequestError, match="credentials"):
            RazorpayService(db, settings(RAZORPAY_KEY_ID="", RAZORPAY_KEY_SECRET="")).create_order(user, order.id)
    finally:
        cleanup(db, user, order)


def test_invalid_signature_is_rejected():
    with pytest.raises(BadRequestError, match="signature"):
        RazorpayService.verify_payment_signature(
            {"razorpay_order_id": "order", "razorpay_payment_id": "pay", "razorpay_signature": "bad"},
            "secret",
        )


def test_valid_signature_is_accepted(monkeypatch):
    monkeypatch.setattr("app.services.razorpay_service.razorpay.Client", lambda auth: SimpleNamespace(utility=SimpleNamespace(verify_payment_signature=lambda payload: None)))
    RazorpayService.verify_payment_signature(
        {"razorpay_order_id": "order", "razorpay_payment_id": "pay", "razorpay_signature": "valid"},
        "secret",
    )


def test_order_id_mismatch_is_rejected(monkeypatch):
    db = SessionLocal(); user, order = make_order(db)
    try:
        service = RazorpayService(db, settings())
        order.payment_provider = "RAZORPAY"; order.provider_order_id = "order_stored"; db.commit()
        with pytest.raises(BadRequestError, match="does not match"):
            asyncio.run(service.verify_payment(user, order.id, RazorpayPaymentVerification(razorpay_order_id="order_other", razorpay_payment_id="pay", razorpay_signature="sig")))
    finally:
        cleanup(db, user, order)


def test_wrong_customer_is_rejected(monkeypatch):
    db = SessionLocal(); user, order = make_order(db); other, other_order = make_order(db)
    try:
        with pytest.raises(NotFoundError):
            RazorpayService(db, settings()).create_order(other, order.id)
    finally:
        cleanup(db, other, other_order, close=False)
        cleanup(db, user, order)


def test_valid_payment_verification_marks_order_paid(monkeypatch):
    db = SessionLocal(); user, order = make_order(db)
    try:
        client = mock_client(monkeypatch, "order_test_123")
        service = RazorpayService(db, settings())
        service.create_order(user, order.id)
        monkeypatch.setattr("app.services.razorpay_service.FulfillmentService.submit", lambda *args: asyncio.sleep(0))
        result = asyncio.run(service.verify_payment(user, order.id, RazorpayPaymentVerification(razorpay_order_id="order_test_123", razorpay_payment_id="pay_test", razorpay_signature="valid")))
        db.refresh(order)
        assert result.payment_status == "PAID"
        assert order.provider_reference == "pay_test"
        assert db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id, PaymentAttempt.provider_payment_id == "pay_test").count() == 1
        assert client.utility.verify_payment_signature.called
    finally:
        cleanup(db, user, order)


def test_duplicate_verification_is_safe(monkeypatch):
    db = SessionLocal(); user, order = make_order(db)
    try:
        mock_client(monkeypatch, "order_test_123")
        service = RazorpayService(db, settings())
        service.create_order(user, order.id)
        monkeypatch.setattr("app.services.razorpay_service.FulfillmentService.submit", lambda *args: asyncio.sleep(0))
        payload = RazorpayPaymentVerification(razorpay_order_id="order_test_123", razorpay_payment_id="pay_test", razorpay_signature="valid")
        asyncio.run(service.verify_payment(user, order.id, payload))
        result = asyncio.run(service.verify_payment(user, order.id, payload))
        assert result.payment_status == "PAID"
        assert db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order.id).count() == 1
    finally:
        cleanup(db, user, order)


def test_already_paid_order_rejects_different_payment(monkeypatch):
    db = SessionLocal(); user, order = make_order(db, status="PAID", payment_status="PAID")
    try:
        order.payment_provider = "RAZORPAY"; order.provider_order_id = "order_test_123"
        db.add(PaymentAttempt(order=order, provider="RAZORPAY", provider_order_id="order_test_123", provider_payment_id="pay_existing", status="CAPTURED")); db.commit()
        with pytest.raises(BadRequestError, match="already been paid"):
            asyncio.run(RazorpayService(db, settings()).verify_payment(user, order.id, RazorpayPaymentVerification(razorpay_order_id="order_test_123", razorpay_payment_id="pay_other", razorpay_signature="valid")))
    finally:
        cleanup(db, user, order)


@pytest.mark.parametrize("status,payment_status", [("CANCELLED", "CANCELLED"), ("REFUNDED", "REFUNDED")])
def test_cancelled_or_refunded_order_rejected(status, payment_status, monkeypatch):
    db = SessionLocal(); user, order = make_order(db, status=status, payment_status=payment_status)
    try:
        with pytest.raises(BadRequestError, match="not payable"):
            RazorpayService(db, settings()).create_order(user, order.id)
    finally:
        cleanup(db, user, order)


def test_non_captured_payment_is_rejected(monkeypatch):
    db = SessionLocal(); user, order = make_order(db)
    try:
        client = mock_client(monkeypatch, "order_test_123")
        service = RazorpayService(db, settings())
        service.create_order(user, order.id)
        client.payment.fetch.return_value["status"] = "failed"
        with pytest.raises(BadRequestError, match="does not match"):
            asyncio.run(service.verify_payment(user, order.id, RazorpayPaymentVerification(razorpay_order_id="order_test_123", razorpay_payment_id="pay_test", razorpay_signature="valid")))
    finally:
        cleanup(db, user, order)


def test_webhook_missing_signature_is_rejected():
    db = SessionLocal()
    try:
        with pytest.raises(BadRequestError, match="signature"):
            asyncio.run(RazorpayService(db, settings()).process_webhook(b'{"event":"payment.failed"}', None))
    finally:
        db.close()


def test_webhook_invalid_signature_is_rejected(monkeypatch):
    db = SessionLocal()
    try:
        monkeypatch.setattr("app.services.razorpay_service.razorpay.Utility.verify_webhook_signature", MagicMock(side_effect=ValueError("invalid")))
        with pytest.raises(BadRequestError, match="signature"):
            asyncio.run(RazorpayService(db, settings()).process_webhook(b'{"event":"payment.failed"}', "bad"))
    finally:
        db.close()


def test_modified_webhook_body_is_rejected():
    db = SessionLocal()
    try:
        body = webhook_body("payment.failed", {"id": "pay_webhook", "order_id": "order_webhook_123"})
        modified = body.replace(b"payment.failed", b"payment.captured")
        with pytest.raises(BadRequestError, match="signature"):
            asyncio.run(RazorpayService(db, settings()).process_webhook(modified, webhook_signature(body)))
    finally:
        db.close()


def test_valid_captured_webhook_consumes_and_fulfills_once(monkeypatch):
    db = SessionLocal(); user, order, attempt = setup_webhook_order(db)
    consume = MagicMock(return_value=True)
    submit = MagicMock(side_effect=lambda *args: asyncio.sleep(0))
    try:
        monkeypatch.setattr("app.services.razorpay_service.InventoryReservationService.consume_for_order", consume)
        monkeypatch.setattr("app.services.razorpay_service.FulfillmentService.submit", submit)
        entity = {"id": "pay_webhook", "order_id": "order_webhook_123", "amount": 41272, "currency": "INR", "status": "captured"}
        body = webhook_body("payment.captured", entity)
        service = RazorpayService(db, settings())
        asyncio.run(service.process_webhook(body, webhook_signature(body)))
        asyncio.run(service.process_webhook(body, webhook_signature(body)))
        db.refresh(order)
        assert order.payment_status == "PAID"
        assert order.status == "PAID"
        assert consume.call_count == 1
        assert submit.call_count == 1
        assert attempt.status == "CAPTURED"
    finally:
        cleanup(db, user, order)


def test_captured_webhook_wrong_payment_relationship_is_rejected():
    db = SessionLocal(); user, order, _ = setup_webhook_order(db, payment_id="pay_expected")
    try:
        entity = {"id": "pay_other", "order_id": "order_webhook_123", "amount": 41272, "currency": "INR", "status": "captured"}
        body = webhook_body("payment.captured", entity)
        with pytest.raises(BadRequestError, match="does not match"):
            asyncio.run(RazorpayService(db, settings()).process_webhook(body, webhook_signature(body)))
    finally:
        cleanup(db, user, order)


@pytest.mark.parametrize("field,value", [("amount", 1), ("currency", "USD")])
def test_captured_webhook_wrong_amount_or_currency_is_rejected(field, value):
    db = SessionLocal(); user, order, _ = setup_webhook_order(db)
    try:
        entity = {"id": "pay_webhook", "order_id": "order_webhook_123", "amount": 41272, "currency": "INR", "status": "captured"}
        entity[field] = value
        body = webhook_body("payment.captured", entity)
        with pytest.raises(BadRequestError, match="does not match"):
            asyncio.run(RazorpayService(db, settings()).process_webhook(body, webhook_signature(body)))
    finally:
        cleanup(db, user, order)


def test_failed_webhook_marks_failed_and_releases_reservation(monkeypatch):
    db = SessionLocal(); user, order, attempt = setup_webhook_order(db)
    release = MagicMock(return_value=1)
    try:
        monkeypatch.setattr("app.services.razorpay_service.InventoryReservationService.release_for_order", release)
        entity = {"id": "pay_webhook", "order_id": "order_webhook_123", "amount": 41272, "currency": "INR", "error_description": "declined"}
        body = webhook_body("payment.failed", entity)
        asyncio.run(RazorpayService(db, settings()).process_webhook(body, webhook_signature(body)))
        db.refresh(order)
        assert order.payment_status == "FAILED"
        assert order.status == "PENDING_PAYMENT"
        assert attempt.status == "FAILED"
        release.assert_called_once_with(order.id)
    finally:
        cleanup(db, user, order)


@pytest.mark.parametrize(
    "event,expected_status,expected_payment_status",
    [("refund.processed", "SUCCESS", "REFUNDED"), ("refund.failed", "FAILED", "REFUND_FAILED")],
)
def test_refund_webhooks_update_existing_refund(event, expected_status, expected_payment_status):
    db = SessionLocal(); user, order, attempt = setup_webhook_order(db)
    refund = RefundRequest(
        order=order,
        payment_attempt=attempt,
        provider="RAZORPAY",
        provider_order_id=order.provider_order_id,
        amount=order.total,
        currency="INR",
        status="PROCESSING",
        idempotency_key=f"refund-{order.id}",
        requested_by="customer",
    )
    db.add(refund); db.commit()
    try:
        entity = {"id": "rfnd_webhook", "payment_id": "pay_webhook", "amount": 41272, "currency": "INR"}
        body = refund_webhook_body(event, entity)
        service = RazorpayService(db, settings())
        asyncio.run(service.process_webhook(body, webhook_signature(body)))
        asyncio.run(service.process_webhook(body, webhook_signature(body)))
        db.refresh(refund); db.refresh(order)
        assert refund.status == expected_status
        assert order.payment_status == expected_payment_status
    finally:
        cleanup(db, user, order)