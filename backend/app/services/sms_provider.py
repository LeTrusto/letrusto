from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx

from app.core.config import get_settings
from app.core.exceptions import BadRequestError


class SmsProvider(Protocol):
    def send_otp(self, mobile_number: str, otp: str) -> None: ...


@dataclass
class SentOtp:
    mobile_number: str
    otp: str


class MockSmsProvider:
    sent: list[SentOtp] = []

    def send_otp(self, mobile_number: str, otp: str) -> None:
        self.sent.append(SentOtp(mobile_number=mobile_number, otp=otp))


class ConfiguredSmsProvider:
    def send_otp(self, mobile_number: str, otp: str) -> None:
        settings = get_settings()
        if not settings.SMS_API_URL or not settings.SMS_API_KEY or not settings.SMS_SENDER_ID:
            raise BadRequestError("SMS provider integration is not configured")
        try:
            response = httpx.post(
                settings.SMS_API_URL,
                headers={"Authorization": f"Bearer {settings.SMS_API_KEY}"},
                json={
                    "to": mobile_number,
                    "sender": settings.SMS_SENDER_ID,
                    "message": f"Your LeTrusto OTP is {otp}. It expires in {settings.OTP_EXPIRE_MINUTES} minutes.",
                },
                timeout=10,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise BadRequestError("Unable to send OTP") from exc


def get_sms_provider() -> SmsProvider:
    settings = get_settings()
    if settings.SMS_PROVIDER == "mock":
        if settings.APP_ENV == "production":
            raise BadRequestError("Production SMS provider is not configured")
        return MockSmsProvider()
    return ConfiguredSmsProvider()
