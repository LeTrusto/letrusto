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


def _html_document(
    preheader: str,
    body: str,
    logo_url: str = "https://letrusto.com/images/logo/logo.png",
    website_url: str = "https://letrusto.com",
) -> str:
    return (
        "<!doctype html>"
        '<html lang="en">'
        '  <body style="margin:0;background:#f1f5f9;padding:0;font-family:Segoe UI,Arial,Helvetica,sans-serif;color:#0f172a;">'
        f'    <div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent;">{escape(preheader)}</div>'
        '    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f1f5f9;padding:32px 16px;">'
        '      <tr>'
        '        <td align="center">'
        '          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:700px;background:#ffffff;border:1px solid #dbe4ee;border-radius:18px;overflow:hidden;">'
        '            <tr>'
        '              <td style="padding:24px 32px 18px 32px;background:#0f172a;">'
        f'                <img src="{escape(logo_url)}" alt="LeTrusto" width="160" style="display:block;height:auto;max-width:160px;margin:0;" />'
        '              </td>'
        '            </tr>'
        '            <tr>'
        f'              <td style="padding:32px;">{body}</td>'
        '            </tr>'
        '          </table>'
        '          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:700px;">'
        '            <tr>'
        '              <td style="padding:16px 12px 0 12px;text-align:center;color:#64748b;font-size:12px;line-height:1.6;">'
        '                This email was generated automatically by LeTrusto.<br />'
        f'                © LeTrusto • <a href="{escape(website_url)}" style="color:#1d4ed8;text-decoration:none;">LeTrusto</a>'
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
    customer_email = str(context["customer_email"])
    mailto_link = f"mailto:{escape(customer_email)}"

    rows = "".join(
        [
            _render_label_value("Ticket ID", f"#{context['ticket_id']}"),
            _render_label_value("Customer Name", str(context['customer_name'])),
            _render_label_value("Customer Email", customer_email),
            _render_label_value("Subject", str(context['subject'])),
            _render_label_value("Message", str(context['message'])),
            _render_label_value("Submitted Time", str(context['created_time'])),
        ]
    )
    html = _html_document(
        f"New support ticket #{context['ticket_id']} from {context['customer_email']}",
        (
            '<h1 style="margin:0 0 10px 0;font-size:27px;line-height:1.2;color:#0f172a;">New Support Ticket</h1>'
            '<p style="margin:0 0 22px 0;font-size:15px;line-height:1.7;color:#475569;">'
            "A new support request was submitted on LeTrusto."
            "</p>"
            '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;">'
            '<tr><td style="padding:18px 20px;">'
            '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;">'
            f"{rows}"
            "</table>"
            "</td></tr></table>"
            '<div style="margin-top:24px;text-align:left;">'
            f'<a href="{mailto_link}" style="display:inline-block;background:#1d4ed8;color:#ffffff;text-decoration:none;font-size:14px;font-weight:600;padding:12px 18px;border-radius:8px;">Reply to Customer</a>'
            "</div>"
            '<div style="margin-top:18px;padding:14px 16px;border-radius:10px;background:#f8fafc;border:1px solid #e2e8f0;color:#475569;font-size:13px;line-height:1.7;">'
            f"Support Inbox: {escape(str(context['support_email']))}<br />"
            "This email was generated automatically by LeTrusto."
            '</div>'
        ),
        logo_url=str(context.get("logo_url", "https://letrusto.com/images/logo/logo.png")),
        website_url=str(context.get("website_url", "https://letrusto.com")),
    )
    text = _text_block(
        [
            f"New Support Ticket #{context['ticket_id']}",
            f"Customer Name: {context['customer_name']}",
            f"Customer Email: {context['customer_email']}",
            f"Subject: {context['subject']}",
            f"Message: {context['message']}",
            f"Submitted Time: {context['created_time']}",
            f"Support Inbox: {context['support_email']}",
            f"Reply: mailto:{context['customer_email']}",
            "This email was generated automatically by LeTrusto.",
        ]
    )
    return RenderedEmail(subject=subject, html=html, text=text)


def _support_confirmation_template(context: Mapping[str, Any]) -> RenderedEmail:
    subject = "We've received your request – LeTrusto Support"
    html = _html_document(
        f"LeTrusto Support received ticket #{context['ticket_id']}",
        (
            '<h1 style="margin:0 0 10px 0;font-size:27px;line-height:1.2;color:#0f172a;">Thank You for Contacting LeTrusto</h1>'
            '<p style="margin:0 0 20px 0;font-size:15px;line-height:1.7;color:#475569;">'
            "Your support request has been received successfully."
            "</p>"
            '<div style="padding:18px 20px;border-radius:12px;background:#f8fafc;border:1px solid #e2e8f0;">'
            '<p style="margin:0 0 8px 0;font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#64748b;">Ticket Confirmation</p>'
            f"<p style='margin:0;font-size:18px;line-height:1.5;color:#0f172a;font-weight:700;'>Ticket #{escape(str(context['ticket_id']))}</p>"
            '</div>'
            '<div style="margin-top:16px;padding:18px 20px;border-radius:12px;border:1px solid #e2e8f0;">'
            f"<p style='margin:0 0 8px 0;font-size:14px;color:#0f172a;'><strong>Subject:</strong> {escape(str(context['subject']))}</p>"
            f"<p style='margin:0;font-size:14px;color:#475569;'><strong>Submitted Time:</strong> {escape(str(context['created_time']))}</p>"
            '</div>'
            '<div style="margin-top:18px;padding:16px 18px;border-radius:10px;background:#eff6ff;border:1px solid #bfdbfe;">'
            f"<p style='margin:0 0 10px 0;font-size:14px;line-height:1.7;color:#0f172a;'>If you need to add more details, reply to this email or write to <a href='mailto:{escape(str(context['support_email']))}' style='color:#4f46e5;text-decoration:none;font-weight:700;'>{escape(str(context['support_email']))}</a>.</p>"
            f"<p style='margin:0;font-size:14px;line-height:1.7;color:#0f172a;'>We will review the request and follow up using the contact information provided.</p>"
            '</div>'
            '<div style="margin-top:16px;color:#64748b;font-size:12px;line-height:1.6;">'
            "This email was generated automatically by LeTrusto."
            '</div>'
        ),
        logo_url=str(context.get("logo_url", "https://letrusto.com/images/logo/logo.png")),
        website_url=str(context.get("website_url", "https://letrusto.com")),
    )
    text = _text_block(
        [
            "We've received your request – LeTrusto Support",
            f"Ticket ID: #{context['ticket_id']}",
            "Thank you for contacting LeTrusto.",
            f"Subject: {context['subject']}",
            f"Submitted Time: {context['created_time']}",
            f"Support email: {context['support_email']}",
            f"Website: {context['website_url']}",
            "This email was generated automatically by LeTrusto.",
        ]
    )
    return RenderedEmail(subject=subject, html=html, text=text)


def _email_verification_template(context: Mapping[str, Any]) -> RenderedEmail:
    verification_url = str(context["verification_url"])
    html = _html_document(
        "Verify your LeTrusto email address",
        (
            '<h1 style="margin:0 0 10px 0;font-size:27px;line-height:1.2;color:#0f172a;">Verify your email address</h1>'
            '<p style="margin:0 0 22px 0;font-size:15px;line-height:1.7;color:#475569;">Welcome to LeTrusto. Confirm your email address to finish setting up your account.</p>'
            f'<a href="{escape(verification_url)}" style="display:inline-block;background:#1d4ed8;color:#ffffff;text-decoration:none;font-size:14px;font-weight:600;padding:12px 18px;border-radius:8px;">Verify email</a>'
            '<p style="margin:22px 0 0 0;font-size:13px;line-height:1.7;color:#64748b;">This link expires in 30 minutes. If you did not create this account, you can ignore this email.</p>'
        ),
        logo_url=str(context.get("logo_url", "https://letrusto.com/images/logo/logo.png")),
        website_url=str(context.get("website_url", "https://letrusto.com")),
    )
    text = _text_block(
        [
            "Verify your LeTrusto email address",
            "Welcome to LeTrusto. Confirm your email address to finish setting up your account.",
            f"Verify your email: {verification_url}",
            "This link expires in 30 minutes.",
            "If you did not create this account, you can ignore this email.",
        ]
    )
    return RenderedEmail(subject="Verify your LeTrusto email", html=html, text=text)


def _password_reset_template(context: Mapping[str, Any]) -> RenderedEmail:
    reset_url = str(context["reset_url"])
    html = _html_document(
        "Reset your LeTrusto password",
        (
            '<h1 style="margin:0 0 10px 0;font-size:27px;line-height:1.2;color:#0f172a;">Reset your password</h1>'
            '<p style="margin:0 0 22px 0;font-size:15px;line-height:1.7;color:#475569;">We received a request to reset your LeTrusto password.</p>'
            f'<a href="{escape(reset_url)}" style="display:inline-block;background:#1d4ed8;color:#ffffff;text-decoration:none;font-size:14px;font-weight:600;padding:12px 18px;border-radius:8px;">Reset password</a>'
            '<p style="margin:22px 0 0 0;font-size:13px;line-height:1.7;color:#64748b;">This link expires in 30 minutes. If you did not request a reset, you can ignore this email.</p>'
        ),
        logo_url=str(context.get("logo_url", "https://letrusto.com/images/logo/logo.png")),
        website_url=str(context.get("website_url", "https://letrusto.com")),
    )
    text = _text_block(
        [
            "Reset your LeTrusto password",
            "We received a request to reset your LeTrusto password.",
            f"Reset your password: {reset_url}",
            "This link expires in 30 minutes.",
            "If you did not request a reset, you can ignore this email.",
        ]
    )
    return RenderedEmail(subject="Reset your LeTrusto password", html=html, text=text)


def _order_confirmation_template(context: Mapping[str, Any]) -> RenderedEmail:
    order_number = str(context["order_number"])
    customer_name = str(context["customer_name"])
    total = str(context["total"])
    currency = str(context.get("currency", "INR"))
    order_url = str(context.get("order_url", ""))
    html = _html_document(
        f"Payment confirmed for LeTrusto order {order_number}",
        (
            '<h1 style="margin:0 0 10px 0;font-size:27px;line-height:1.2;color:#0f172a;">Order confirmed</h1>'
            f'<p style="margin:0 0 22px 0;font-size:15px;line-height:1.7;color:#475569;">Thank you, {escape(customer_name)}. We received your payment and are preparing your order.</p>'
            '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;border:1px solid #e2e8f0;">'
            '<tr><td style="padding:18px 20px;"><table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;">'
            f"{_render_label_value('Order number', order_number)}"
            f"{_render_label_value('Amount paid', f'{currency} {total}')}"
            '</table></td></tr></table>'
            + (f'<div style="margin-top:24px;"><a href="{escape(order_url)}" style="display:inline-block;background:#1d4ed8;color:#ffffff;text-decoration:none;font-size:14px;font-weight:600;padding:12px 18px;border-radius:8px;">View order</a></div>' if order_url else '')
        ),
        logo_url=str(context.get("logo_url", "https://letrusto.com/images/logo/logo.png")),
        website_url=str(context.get("website_url", "https://letrusto.com")),
    )
    text_lines = [
        "Order confirmed",
        f"Thank you, {customer_name}. We received your payment and are preparing your order.",
        f"Order number: {order_number}",
        f"Amount paid: {currency} {total}",
    ]
    if order_url:
        text_lines.append(f"View order: {order_url}")
    text_lines.append("This email was generated automatically by LeTrusto.")
    return RenderedEmail(subject=f"Order confirmed: {order_number}", html=html, text=_text_block(text_lines))


def _digital_purchase_template(context: Mapping[str, Any]) -> RenderedEmail:
    product_name = str(context["product_name"])
    amount = str(context["amount"])
    reference = str(context["reference"])
    purchased_at = str(context["purchased_at"])
    download_url = str(context["download_url"])
    purchases_url = str(context["purchases_url"])
    support_url = str(context["support_url"])
    html = _html_document(
        "Payment successful | LeTrusto",
        (
            '<h1 style="margin:0 0 10px 0;font-size:27px;line-height:1.2;color:#0f172a;">Payment successful</h1>'
            '<p style="margin:0 0 22px 0;font-size:15px;line-height:1.7;color:#475569;">Your LeTrusto toolkit is ready.</p>'
            '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;border:1px solid #e2e8f0;">'
            '<tr><td style="padding:18px 20px;"><table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;">'
            f"{_render_label_value('Product', product_name)}{_render_label_value('Amount paid', f'INR {amount}')}{_render_label_value('Reference', reference)}{_render_label_value('Date', purchased_at)}"
            '</table></td></tr></table>'
            f'<div style="margin-top:24px;"><a href="{escape(download_url)}" style="display:inline-block;background:#1d4ed8;color:#ffffff;text-decoration:none;font-size:14px;font-weight:600;padding:12px 18px;border-radius:8px;">Download toolkit</a></div>'
            f'<p style="margin:20px 0 0 0;font-size:14px;line-height:1.7;color:#475569;"><a href="{escape(purchases_url)}" style="color:#1d4ed8;">My Purchases</a> · <a href="{escape(support_url)}" style="color:#1d4ed8;">Contact Support</a></p>'
        ),
        logo_url=str(context.get("logo_url", "https://letrusto.com/images/logo/logo.png")),
        website_url=str(context.get("website_url", "https://letrusto.com")),
    )
    return RenderedEmail(subject=f"Payment successful: {product_name}", html=html, text=_text_block([
        "Payment successful", "Your LeTrusto toolkit is ready.", f"Product: {product_name}",
        f"Amount paid: INR {amount}", f"Reference: {reference}", f"Date: {purchased_at}",
        f"Download toolkit: {download_url}", f"My Purchases: {purchases_url}", f"Contact Support: {support_url}",
    ]))


def _shipment_template(context: Mapping[str, Any]) -> RenderedEmail:
    status = str(context["status"])
    order_number = str(context["order_number"])
    customer_name = str(context["customer_name"])
    items_summary = str(context["items_summary"])
    tracking_number = str(context.get("tracking_number") or "")
    carrier = str(context.get("carrier") or "")
    tracking_url = str(context.get("tracking_url") or "")
    delivered = status == "delivered"
    title = "Your order was delivered" if delivered else "Your order has shipped"
    message = "Your LeTrusto order has been delivered." if delivered else "Your LeTrusto order is on the way."
    tracking_rows = ""
    if tracking_number:
        tracking_rows += _render_label_value("Tracking number", tracking_number)
    if carrier:
        tracking_rows += _render_label_value("Carrier", carrier)
    html = _html_document(
        f"{title}: {order_number}",
        (
            f'<h1 style="margin:0 0 10px 0;font-size:27px;line-height:1.2;color:#0f172a;">{title}</h1>'
            f'<p style="margin:0 0 22px 0;font-size:15px;line-height:1.7;color:#475569;">{escape(customer_name)}, {escape(message)}</p>'
            '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;border:1px solid #e2e8f0;">'
            '<tr><td style="padding:18px 20px;"><table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;">'
            f"{_render_label_value('Order number', order_number)}"
            f"{_render_label_value('Items', items_summary)}"
            f"{tracking_rows}"
            '</table></td></tr></table>'
            + (f'<div style="margin-top:24px;"><a href="{escape(tracking_url)}" style="display:inline-block;background:#1d4ed8;color:#ffffff;text-decoration:none;font-size:14px;font-weight:600;padding:12px 18px;border-radius:8px;">Track shipment</a></div>' if tracking_url else '')
            + (f'<p style="margin:18px 0 0 0;font-size:13px;color:#64748b;">View your order at <a href="{escape(str(context["order_url"]))}" style="color:#1d4ed8;">LeTrusto</a>.</p>' if context.get("order_url") else '')
        ),
        logo_url=str(context.get("logo_url", "https://letrusto.com/images/logo/logo.png")),
        website_url=str(context.get("website_url", "https://letrusto.com")),
    )
    text_lines = [title, message, f"Order number: {order_number}", f"Items: {items_summary}"]
    if tracking_number:
        text_lines.append(f"Tracking number: {tracking_number}")
    if carrier:
        text_lines.append(f"Carrier: {carrier}")
    if tracking_url:
        text_lines.append(f"Track shipment: {tracking_url}")
    if context.get("order_url"):
        text_lines.append(f"View order: {context['order_url']}")
    text_lines.append("This email was generated automatically by LeTrusto.")
    return RenderedEmail(subject=f"{title}: {order_number}", html=html, text=_text_block(text_lines))


def _shipped_template(context: Mapping[str, Any]) -> RenderedEmail:
    return _shipment_template({**context, "status": "shipped"})


def _delivered_template(context: Mapping[str, Any]) -> RenderedEmail:
    return _shipment_template({**context, "status": "delivered"})


def _operational_alert_template(context: Mapping[str, Any]) -> RenderedEmail:
    subject = str(context["subject"])
    rows = "".join(_render_label_value(str(label), str(value)) for label, value in context["details"])
    html = _html_document(
        subject,
        (
            f'<h1 style="margin:0 0 10px 0;font-size:27px;line-height:1.2;color:#0f172a;">{escape(subject)}</h1>'
            '<p style="margin:0 0 22px 0;font-size:15px;line-height:1.7;color:#475569;">'
            "Operational attention is required for the LeTrusto commerce backend."
            "</p>"
            '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;">'
            f"{rows}</table>"
        ),
    )
    text = _text_block([subject, "", *[f"{label}: {value}" for label, value in context["details"]]])
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
        registry.register("email_verification", _email_verification_template)
        registry.register("password_reset", _password_reset_template)
        registry.register("order_confirmation", _order_confirmation_template)
        registry.register("digital_purchase_confirmation", _digital_purchase_template)
        registry.register("order_shipped", _shipped_template)
        registry.register("order_delivered", _delivered_template)
        registry.register("operational_alert", _operational_alert_template)
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
                            "from_email": sender,
                            "attempt": attempt,
                        },
                    )
                    raise EmailDeliveryError(str(exc)) from exc

                logger.warning(
                    "Email delivery attempt failed; retrying",
                    extra={
                        "template": template_name,
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
