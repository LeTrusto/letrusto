from dataclasses import dataclass

import pytest

from app.services.email_service import EmailDeliveryError, EmailService


@dataclass
class SentEmail:
    from_email: str
    to: str | list[str]
    subject: str
    html: str
    text: str
    reply_to: str | list[str] | None


class FakeTransport:
    def __init__(self, failures: int = 0) -> None:
        self.failures = failures
        self.sent: list[SentEmail] = []

    def send(self, **kwargs):
        if self.failures:
            self.failures -= 1
            raise RuntimeError("provider unavailable")
        self.sent.append(SentEmail(**kwargs))
        return {"id": "test-email"}


def test_auth_templates_use_configured_url_and_plain_text_fallback():
    transport = FakeTransport()
    service = EmailService(
        transport=transport,
        from_email="support@letrusto.com",
        default_reply_to="hello@letrusto.com",
        retry_delay_seconds=0,
    )

    service.send_template(
        "email_verification",
        to="customer@example.com",
        context={"verification_url": "https://shop.example/verify-email?token=opaque", "website_url": "https://shop.example"},
    )
    service.send_template(
        "password_reset",
        to="customer@example.com",
        context={"reset_url": "https://shop.example/reset-password?token=opaque", "website_url": "https://shop.example"},
    )

    assert len(transport.sent) == 2
    assert all(email.to == "customer@example.com" for email in transport.sent)
    assert all('href="https://shop.example"' in email.html for email in transport.sent)
    assert all('href="https://letrusto.com"' not in email.html for email in transport.sent)
    assert all("opaque" in email.text for email in transport.sent)
    assert all(email.reply_to == "hello@letrusto.com" for email in transport.sent)


def test_email_delivery_retries_transient_provider_failure():
    transport = FakeTransport(failures=2)
    service = EmailService(transport=transport, from_email="support@letrusto.com", retry_delay_seconds=0, max_retries=2)

    service.send_template(
        "email_verification",
        to="customer@example.com",
        context={"verification_url": "https://shop.example/verify-email?token=opaque"},
    )

    assert len(transport.sent) == 1


def test_email_delivery_failure_is_safely_wrapped():
    transport = FakeTransport(failures=3)
    service = EmailService(transport=transport, from_email="support@letrusto.com", retry_delay_seconds=0, max_retries=2)

    with pytest.raises(EmailDeliveryError, match="provider unavailable"):
        service.send_template(
            "password_reset",
            to="customer@example.com",
            context={"reset_url": "https://shop.example/reset-password?token=opaque"},
        )

    assert not transport.sent


def test_shipment_templates_include_order_tracking_and_public_links():
    transport = FakeTransport()
    service = EmailService(transport=transport, from_email="support@letrusto.com", retry_delay_seconds=0)

    service.send_template(
        "order_shipped",
        to="buyer@example.com",
        context={
            "customer_name": "Buyer",
            "order_number": "LT-1001",
            "items_summary": "Hoodie x1",
            "tracking_number": "TRACK-1",
            "carrier": "Printful Carrier",
            "tracking_url": "https://carrier.example/track/TRACK-1",
            "order_url": "https://letrusto.com/orders/order-1",
        },
    )
    service.send_template(
        "order_delivered",
        to="buyer@example.com",
        context={
            "customer_name": "Buyer",
            "order_number": "LT-1001",
            "items_summary": "Hoodie x1",
            "order_url": "https://letrusto.com/orders/order-1",
        },
    )

    assert [email.to for email in transport.sent] == ["buyer@example.com", "buyer@example.com"]
    assert "LT-1001" in transport.sent[0].text
    assert "https://carrier.example/track/TRACK-1" in transport.sent[0].text
    assert "https://letrusto.com/orders/order-1" in transport.sent[0].text
    assert "LT-1001" in transport.sent[1].text