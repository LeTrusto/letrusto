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
        registry.register("email_verification", _email_verification_template)
        registry.register("password_reset", _password_reset_template)
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
