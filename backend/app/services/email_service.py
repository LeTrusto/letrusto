from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from html import escape
from typing import Any, Callable, Mapping, Protocol

import resend

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RenderedEmail:
    subject: str
    html: str
    text: str


@dataclass(frozen=True)
class SupportTicketEmailContext:
    ticket_id: int
    customer_name: str
    customer_email: str
    subject: str
    category: str
    priority: str
    message: str
    created_time: str
    browser: str
    platform: str
    ip: str
    support_email: str
    website_url: str
    logo_url: str


class EmailTransport(Protocol):
    def send(
        self,
        *,
        from_email: str,
        to: str | list[str],
        subject: str,
        html: str,
        text: str,
        reply_to: str | list[str] | None = None,
    ) -> Any:
        ...


class EmailDeliveryError(RuntimeError):
    pass


class EmailTemplateRegistry:
    def __init__(self) -> None:
        self._templates: dict[str, Callable[[Mapping[str, Any]], RenderedEmail]] = {}

    def register(self, name: str, renderer: Callable[[Mapping[str, Any]], RenderedEmail]) -> None:
        self._templates[name] = renderer

    def render(self, name: str, context: Mapping[str, Any]) -> RenderedEmail:
        renderer = self._templates.get(name)
        if renderer is None:
            raise ValueError(f"Unknown email template: {name}")
        return renderer(context)


def _render_label_value(label: str, value: str) -> str:
    return (
        "<tr>"
        f"<td style='padding:10px 0;color:#64748b;font-size:13px;font-weight:600;vertical-align:top;width:165px;'>{escape(label)}</td>"
        f"<td style='padding:10px 0;color:#0f172a;font-size:14px;line-height:1.6;vertical-align:top;'>{escape(value)}</td>"
        "</tr>"
    )


def _html_document(preheader: str, body: str) -> str:
    return (
        "<!doctype html>"
        '<html lang="en">'
        '  <body style="margin:0;background:#f8fafc;padding:0;font-family:Arial,Helvetica,sans-serif;color:#0f172a;">'
        f'    <div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent;">{escape(preheader)}</div>'
        '    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f8fafc;padding:32px 16px;">'
        '      <tr>'
        '        <td align="center">'
        '          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:680px;background:#ffffff;border:1px solid #e2e8f0;border-radius:24px;overflow:hidden;">'
        '            <tr>'
        '              <td style="padding:28px 32px 12px 32px;background:linear-gradient(135deg,#0f172a 0%,#312e81 50%,#ec4899 100%);">'
        '                <img src="https://letrusto.com/images/logo/logo.png" alt="LeTrusto" width="160" style="display:block;height:auto;max-width:160px;margin:0 0 8px 0;" />'
        '              </td>'
        '            </tr>'
        '            <tr>'
        f'              <td style="padding:32px;">{body}</td>'
        '            </tr>'
        '          </table>'
        '          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:680px;">'
        '            <tr>'
        '              <td style="padding:16px 12px 0 12px;text-align:center;color:#64748b;font-size:12px;line-height:1.6;">'
        '                © LeTrusto • <a href="https://letrusto.com" style="color:#4f46e5;text-decoration:none;">letrusto.com</a>'
        '              </td>'
        '            </tr>'
        '          </table>'
        '        </td>'
        '      </tr>'
        '    </table>'
        '  </body>'
        '</html>'
    )


def _text_block(lines: list[str]) -> str:
    return "\n".join(lines)


def _support_admin_template(context: Mapping[str, Any]) -> RenderedEmail:
    subject = f"[LeTrusto Support] Ticket #{context['ticket_id']} - {context['subject']}"
    rows = "".join(
        [
            _render_label_value("Ticket ID", f"#{context['ticket_id']}"),
            _render_label_value("Customer Name", str(context['customer_name'])),
            _render_label_value("Customer Email", str(context['customer_email'])),
            _render_label_value("Subject", str(context['subject'])),
            _render_label_value("Category", str(context['category'])),
            _render_label_value("Priority", str(context['priority'])),
            _render_label_value("Message", str(context['message'])),
            _render_label_value("Created Time", str(context['created_time'])),
            _render_label_value("Browser", str(context['browser'])),
            _render_label_value("Platform", str(context['platform'])),
            _render_label_value("IP", str(context['ip'])),
        ]
    )
    html = _html_document(
        f"New support ticket #{context['ticket_id']} from {context['customer_email']}",
        (
            '<h1 style="margin:0 0 12px 0;font-size:28px;line-height:1.2;color:#0f172a;">New Support Ticket</h1>'
            '<p style="margin:0 0 24px 0;font-size:15px;line-height:1.7;color:#475569;">'
            "A new ticket was submitted on LeTrusto and saved to the database. Review the details below."
            "</p>"
            f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;">{rows}</table>'
            '<div style="margin-top:28px;padding:16px 18px;border-radius:18px;background:#f8fafc;border:1px solid #e2e8f0;color:#475569;font-size:14px;line-height:1.7;">'
            f"<strong style='color:#0f172a;'>Action:</strong> Reply through your support inbox at {escape(str(context['support_email']))}."
            '</div>'
        ),
    )
    text = _text_block(
        [
            f"New Support Ticket #{context['ticket_id']}",
            f"Customer Name: {context['customer_name']}",
            f"Customer Email: {context['customer_email']}",
            f"Subject: {context['subject']}",
            f"Category: {context['category']}",
            f"Priority: {context['priority']}",
            f"Message: {context['message']}",
            f"Created Time: {context['created_time']}",
            f"Browser: {context['browser']}",
            f"Platform: {context['platform']}",
            f"IP: {context['ip']}",
            f"Support Inbox: {context['support_email']}",
        ]
    )
    return RenderedEmail(subject=subject, html=html, text=text)


def _support_confirmation_template(context: Mapping[str, Any]) -> RenderedEmail:
    subject = "We've received your request – LeTrusto Support"
    html = _html_document(
        f"LeTrusto Support received ticket #{context['ticket_id']}",
        (
            '<h1 style="margin:0 0 12px 0;font-size:28px;line-height:1.2;color:#0f172a;">Thanks for contacting LeTrusto</h1>'
            '<p style="margin:0 0 24px 0;font-size:15px;line-height:1.7;color:#475569;">'
            f"We’ve received your request and saved ticket <strong>#{context['ticket_id']}</strong>. "
            "Our team will review it and reply within 24–48 hours."
            "</p>"
            '<div style="padding:20px 22px;border-radius:20px;background:#f8fafc;border:1px solid #e2e8f0;">'
            '<p style="margin:0 0 10px 0;font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#64748b;">Support Summary</p>'
            f"<p style='margin:0;font-size:15px;line-height:1.7;color:#0f172a;'>{escape(str(context['subject']))}</p>"
            f"<p style='margin:12px 0 0 0;font-size:14px;line-height:1.7;color:#475569;'>Category: {escape(str(context['category']))} • Priority: {escape(str(context['priority']))}</p>"
            '</div>'
            '<div style="margin-top:24px;padding:18px 22px;border-radius:20px;background:linear-gradient(135deg,#eef2ff 0%,#fdf2f8 100%);border:1px solid #e2e8f0;">'
            f"<p style='margin:0 0 10px 0;font-size:14px;line-height:1.7;color:#0f172a;'>If you need to add more details, reply to this email or write to <a href='mailto:{escape(str(context['support_email']))}' style='color:#4f46e5;text-decoration:none;font-weight:700;'>{escape(str(context['support_email']))}</a>.</p>"
            f"<p style='margin:0;font-size:14px;line-height:1.7;color:#0f172a;'>Visit <a href='{escape(str(context['website_url']))}' style='color:#4f46e5;text-decoration:none;font-weight:700;'>LeTrusto</a> anytime for comparisons, guides, and AI buying help.</p>"
            '</div>'
        ),
    )
    text = _text_block(
        [
            "We've received your request – LeTrusto Support",
            f"Ticket ID: #{context['ticket_id']}",
            f"Support summary: {context['subject']}",
            f"Category: {context['category']}",
            f"Priority: {context['priority']}",
            "Expected response: 24–48 hours",
            f"Support email: {context['support_email']}",
            f"Website: {context['website_url']}",
        ]
    )
    return RenderedEmail(subject=subject, html=html, text=text)


class EmailService:
    def __init__(
        self,
        *,
        transport: EmailTransport,
        from_email: str,
        default_reply_to: str | None = None,
        template_registry: EmailTemplateRegistry | None = None,
        max_retries: int = 2,
        retry_delay_seconds: float = 0.25,
    ) -> None:
        self.transport = transport
        self.from_email = from_email
        self.default_reply_to = default_reply_to
        self.template_registry = template_registry or self._build_default_registry()
        self.max_retries = max(0, max_retries)
        self.retry_delay_seconds = max(0.0, retry_delay_seconds)

    @classmethod
    def from_settings(cls, settings: Any | None = None) -> EmailService:
        if settings is None:
            from app.core.config import get_settings

            settings = get_settings()

        return cls(
            transport=ResendEmailTransport(api_key=settings.RESEND_API_KEY),
            from_email=settings.FROM_EMAIL,
            default_reply_to=settings.SUPPORT_EMAIL,
        )

    def _build_default_registry(self) -> EmailTemplateRegistry:
        registry = EmailTemplateRegistry()
        registry.register("support_ticket_admin", _support_admin_template)
        registry.register("support_ticket_customer_confirmation", _support_confirmation_template)
        return registry

    def register_template(self, name: str, renderer: Callable[[Mapping[str, Any]], RenderedEmail]) -> None:
        self.template_registry.register(name, renderer)

    def send_template(
        self,
        template_name: str,
        *,
        to: str | list[str],
        context: Mapping[str, Any],
        reply_to: str | list[str] | None = None,
        from_email: str | None = None,
    ) -> Any:
        rendered = self.template_registry.render(template_name, context)
        return self._send(
            to=to,
            subject=rendered.subject,
            html=rendered.html,
            text=rendered.text,
            reply_to=reply_to,
            from_email=from_email,
            template_name=template_name,
        )

    def _send(
        self,
        *,
        to: str | list[str],
        subject: str,
        html: str,
        text: str,
        reply_to: str | list[str] | None = None,
        from_email: str | None = None,
        template_name: str | None = None,
    ) -> Any:
        sender = from_email or self.from_email
        attempts = self.max_retries + 1

        for attempt in range(1, attempts + 1):
            try:
                result = self.transport.send(
                    from_email=sender,
                    to=to,
                    subject=subject,
                    html=html,
                    text=text,
                    reply_to=reply_to or self.default_reply_to,
                )
                logger.info(
                    "Email sent",
                    extra={
                        "template": template_name,
                        "to": to,
                        "from_email": sender,
                        "attempt": attempt,
                    },
                )
                return result
            except Exception as exc:
                if attempt >= attempts:
                    logger.exception(
                        "Email delivery failed",
                        extra={
                            "template": template_name,
                            "to": to,
                            "from_email": sender,
                            "attempt": attempt,
                        },
                    )
                    raise EmailDeliveryError(str(exc)) from exc

                logger.warning(
                    "Email delivery attempt failed; retrying",
                    extra={
                        "template": template_name,
                        "to": to,
                        "from_email": sender,
                        "attempt": attempt,
                        "max_attempts": attempts,
                    },
                )
                if self.retry_delay_seconds:
                    time.sleep(self.retry_delay_seconds * attempt)


class ResendEmailTransport:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key.strip()
        self.client = resend.Emails()

    def send(
        self,
        *,
        from_email: str,
        to: str | list[str],
        subject: str,
        html: str,
        text: str,
        reply_to: str | list[str] | None = None,
    ) -> Any:
        if not self.api_key:
            raise EmailDeliveryError("RESEND_API_KEY is not configured")

        resend.api_key = self.api_key
        params: dict[str, Any] = {
            "from": from_email,
            "to": to,
            "subject": subject,
            "html": html,
            "text": text,
        }
        if reply_to:
            params["reply_to"] = reply_to
        return self.client.send(params)
