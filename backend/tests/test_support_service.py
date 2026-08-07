from __future__ import annotations

from dataclasses import dataclass

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.entities import SupportTicket
from app.schemas.support import SupportTicketRequest
from app.services.email_service import EmailDeliveryError
from app.services.support_service import SupportService


@dataclass
class EmailCall:
    template_name: str
    to: str | list[str]
    context: dict
    reply_to: str | list[str] | None
    from_email: str | None


class FakeEmailService:
    def __init__(self, *, fail_on_call: int | None = None) -> None:
        self.fail_on_call = fail_on_call
        self.calls: list[EmailCall] = []

    def send_template(
        self,
        template_name: str,
        *,
        to: str | list[str],
        context: dict,
        reply_to: str | list[str] | None = None,
        from_email: str | None = None,
    ) -> None:
        self.calls.append(
            EmailCall(
                template_name=template_name,
                to=to,
                context=context,
                reply_to=reply_to,
                from_email=from_email,
            )
        )
        if self.fail_on_call is not None and len(self.calls) == self.fail_on_call:
            raise EmailDeliveryError("simulated delivery failure")


@pytest.fixture()
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    SupportTicket.__table__.create(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_ticket_persists_ticket_and_sends_both_emails(session):
    email_service = FakeEmailService()
    service = SupportService(
        session,
        email_service=email_service,
        support_email="hello@letrusto.com",
        from_email="support@letrusto.com",
        website_url="https://letrusto.com",
    )

    response = service.create_ticket(
        SupportTicketRequest(
            email="customer@example.com",
            category="feedback",
            subject="Feature request",
            body="Please add a dark mode toggle to the support center.",
        ),
        customer_name="Customer One",
        request=None,
    )

    ticket = session.query(SupportTicket).one()

    assert response.status == "open"
    assert ticket.email == "customer@example.com"
    assert ticket.subject == "Feature request"
    assert [call.template_name for call in email_service.calls] == [
        "support_ticket_admin",
        "support_ticket_customer_confirmation",
    ]
    assert email_service.calls[0].to == "hello@letrusto.com"
    assert email_service.calls[1].to == "customer@example.com"
    assert email_service.calls[0].context["customer_name"] == "Customer One"
    assert email_service.calls[0].context["priority"] == "Low"


def test_create_ticket_ignores_email_failures(session):
    email_service = FakeEmailService(fail_on_call=1)
    service = SupportService(
        session,
        email_service=email_service,
        support_email="hello@letrusto.com",
        from_email="support@letrusto.com",
        website_url="https://letrusto.com",
    )

    response = service.create_ticket(
        SupportTicketRequest(
            email="customer@example.com",
            category="report_wrong",
            subject="Wrong price shown",
            body="The listed price for the phone does not match the retailer page.",
        ),
        customer_name=None,
        request=None,
    )

    ticket = session.query(SupportTicket).one()

    assert response.status == "open"
    assert ticket.category == "report_wrong"
    assert [call.template_name for call in email_service.calls] == [
        "support_ticket_admin",
        "support_ticket_customer_confirmation",
    ]


def test_create_ticket_raises_if_database_write_fails(session):
    email_service = FakeEmailService()
    service = SupportService(session, email_service=email_service)

    def raise_commit() -> None:
        raise Exception("database unavailable")

    session.commit = raise_commit  # type: ignore[method-assign]

    with pytest.raises(HTTPException):
        service.create_ticket(
            SupportTicketRequest(
                email="customer@example.com",
                category="other",
                subject="Broken form",
                body="The support form does not submit on mobile Safari.",
            )
        )
