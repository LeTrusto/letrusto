from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import BadRequestError, UnauthorizedError
from app.core.security import (
    create_access_token,
    decode_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.entities import RefreshToken, User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AuthResponse, TokenIntrospectionResponse, TokenResponse


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.settings = get_settings()

    # ── Legacy token helper (kept for backward-compat) ────────────────────────
    def issue_token(self, subject: str) -> TokenResponse:
        token = create_access_token(subject=subject)
        refresh = generate_refresh_token()
        return TokenResponse(
            access_token=token,
            refresh_token=refresh,
            expires_in=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def introspect(self, token: str) -> TokenIntrospectionResponse:
        from app.core.security import TokenPayloadError
        try:
            payload = decode_token(token)
        except Exception as exc:
            raise UnauthorizedError("Invalid or expired token") from exc
        subject = payload.get("sub", "")
        exp = int(payload.get("exp", 0))
        return TokenIntrospectionResponse(subject=subject, expiresAt=exp)

    # ── Real user auth ─────────────────────────────────────────────────────────
    def register(self, email: str, password: str, full_name: str) -> AuthResponse:
        if self.user_repo.get_by_email(email):
            raise BadRequestError("Email already registered")
        hashed = hash_password(password)
        user = self.user_repo.create(email=email, full_name=full_name, password_hash=hashed)
        self.db.commit()
        self.db.refresh(user)
        return self._build_auth_response(user)

    def login(self, email: str, password: str) -> AuthResponse:
        user = self.user_repo.get_by_email(email)
        if not user or not user.password_hash:
            raise UnauthorizedError("Invalid credentials")
        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")
        if not user.is_active:
            raise UnauthorizedError("Account deactivated")
        return self._build_auth_response(user)

    def link_email(self, user: User, email: str, password: str) -> AuthResponse:
        normalized_email = email.lower().strip()
        existing = self.user_repo.get_by_email(normalized_email)
        if existing and existing.id != user.id:
            raise BadRequestError("Email is already linked to another account")
        if user.email and user.email != normalized_email:
            raise BadRequestError("An email is already linked to this account")
        user.email = normalized_email
        user.password_hash = hash_password(password)
        self.db.commit()
        self.db.refresh(user)
        return self._build_auth_response(user)

    def refresh(self, refresh_token_value: str) -> AuthResponse:
        token_hash = hash_refresh_token(refresh_token_value)
        record = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_hash == token_hash, RefreshToken.revoked.is_(False))
            .first()
        )
        if not record:
            raise UnauthorizedError("Invalid or expired refresh token")
        if _as_utc(record.expires_at) < datetime.now(timezone.utc):
            record.revoked = True
            self.db.commit()
            raise UnauthorizedError("Refresh token expired")
        record.revoked = True
        self.db.flush()
        user = self.user_repo.get_by_id(record.user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("Account not found or deactivated")
        self.db.commit()
        return self._build_auth_response(user)

    def logout(self, refresh_token_value: str) -> None:
        token_hash = hash_refresh_token(refresh_token_value)
        record = self.db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
        if record:
            record.revoked = True
            self.db.commit()

    def get_current_user(self, token: str) -> User:
        from app.core.security import TokenPayloadError
        try:
            payload = decode_token(token)
        except Exception as exc:
            raise UnauthorizedError("Invalid or expired token") from exc
        user_id_str = payload.get("sub", "")
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError as exc:
            raise UnauthorizedError("Invalid token subject") from exc
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("User not found")
        return user

    # ── Internal helpers ──────────────────────────────────────────────────────
    def _build_auth_response(self, user: User) -> AuthResponse:
        access_token = create_access_token(
            subject=str(user.id),
            extra={"role": user.role, "email": user.email or ""},
        )
        refresh_token_value = generate_refresh_token()
        expires_at = datetime.now(timezone.utc) + timedelta(days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS)
        record = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token_value),
            expires_at=expires_at,
        )
        self.db.add(record)
        self.db.commit()
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token_value,
            expires_in=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            avatar_url=user.avatar_url,
        )
