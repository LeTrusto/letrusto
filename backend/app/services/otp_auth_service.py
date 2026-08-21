from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import BadRequestError, UnauthorizedError
from app.core.security import hash_password
from app.models.entities import OtpChallenge, User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.sms_provider import SmsProvider, get_sms_provider


def normalize_indian_mobile(value: str) -> str:
    digits = "".join(character for character in value.strip() if character.isdigit())
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if len(digits) != 10 or digits[0] not in "6789":
        raise BadRequestError("Enter a valid Indian mobile number")
    return f"+91{digits}"


def _hash_otp(mobile_number: str, otp: str) -> str:
    settings = get_settings()
    return hashlib.sha256(f"{settings.JWT_SECRET_KEY}:{mobile_number}:{otp}".encode()).hexdigest()


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


class OtpAuthService:
    def __init__(self, db: Session, sms_provider: SmsProvider | None = None) -> None:
        self.db = db
        self.settings = get_settings()
        self.user_repo = UserRepository(db)
        self.sms_provider = sms_provider or get_sms_provider()

    def request_otp(self, mobile_number: str, request_ip: str | None = None) -> None:
        normalized = normalize_indian_mobile(mobile_number)
        now = datetime.now(timezone.utc)
        latest = (
            self.db.query(OtpChallenge)
            .filter(OtpChallenge.mobile_number == normalized)
            .order_by(OtpChallenge.created_at.desc())
            .first()
        )
        if latest and latest.created_at:
            created_at = _as_utc(latest.created_at)
            if (now - created_at).total_seconds() < self.settings.OTP_RESEND_COOLDOWN_SECONDS:
                raise BadRequestError("Please wait before requesting another OTP")

        hour_ago = now - timedelta(hours=1)
        recent_count = (
            self.db.query(OtpChallenge)
            .filter(OtpChallenge.mobile_number == normalized, OtpChallenge.created_at >= hour_ago)
            .count()
        )
        if recent_count >= self.settings.OTP_MAX_REQUESTS_PER_HOUR:
            raise BadRequestError("Too many OTP requests. Please try again later")

        otp = f"{secrets.randbelow(1_000_000):06d}"
        challenge = OtpChallenge(
            mobile_number=normalized,
            code_hash=_hash_otp(normalized, otp),
            expires_at=now + timedelta(minutes=self.settings.OTP_EXPIRE_MINUTES),
            request_ip=request_ip,
        )
        self.db.add(challenge)
        self.db.commit()
        self.sms_provider.send_otp(normalized, otp)

    def verify_otp(self, mobile_number: str, otp: str):
        normalized = normalize_indian_mobile(mobile_number)
        challenge = (
            self.db.query(OtpChallenge)
            .filter(OtpChallenge.mobile_number == normalized, OtpChallenge.consumed_at.is_(None))
            .order_by(OtpChallenge.created_at.desc())
            .first()
        )
        now = datetime.now(timezone.utc)
        if not challenge or _as_utc(challenge.expires_at) < now:
            raise UnauthorizedError("Invalid or expired OTP")
        if challenge.attempts >= self.settings.OTP_MAX_ATTEMPTS:
            raise UnauthorizedError("OTP verification limit exceeded")
        challenge.attempts += 1
        if not secrets.compare_digest(challenge.code_hash, _hash_otp(normalized, otp)):
            self.db.commit()
            raise UnauthorizedError("Invalid or expired OTP")

        challenge.consumed_at = now
        user = self.user_repo.get_by_mobile(normalized)
        if user and user.role != "user":
            self.db.commit()
            raise UnauthorizedError("Invalid or expired OTP")
        if not user:
            user = self.user_repo.create(email=None, full_name="", mobile_number=normalized)
        self.db.commit()
        self.db.refresh(user)
        return AuthService(self.db)._build_auth_response(user)
