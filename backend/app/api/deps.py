import uuid

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError
from app.db.session import SessionLocal, get_db  # noqa: F401 — re-exported for endpoints
from app.models.entities import User
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.notification_service import NotificationService
from app.services.user_service import UserService
from app.storage import MockObjectStorage, ObjectStorage, S3ObjectStorage


settings = get_settings()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


def get_email_service() -> EmailService:
    return EmailService.from_settings(settings)


def get_storage() -> ObjectStorage:
    if settings.STORAGE_PROVIDER.lower() == "s3":
        if settings.APP_ENV == "production" and (
            not settings.STORAGE_BUCKET
            or not settings.STORAGE_ACCESS_KEY
            or not settings.STORAGE_SECRET_KEY
            or not settings.STORAGE_PUBLIC_BASE_URL.startswith("https://")
        ):
            raise RuntimeError("FATAL: production media storage requires an S3-compatible provider and HTTPS public base URL.")
        return S3ObjectStorage(settings)
    if settings.APP_ENV != "production":
        return MockObjectStorage()
    raise RuntimeError("Production media storage is not configured")


def _extract_bearer(authorization: str) -> str:
    if not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise UnauthorizedError("Missing bearer token")
    return token


def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User:
    token = _extract_bearer(authorization)
    return AuthService(db).get_current_user(token)


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise UnauthorizedError("Admin access required")
    return current_user


def get_optional_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User | None:
    if not authorization:
        return None
    try:
        token = _extract_bearer(authorization)
        return AuthService(db).get_current_user(token)
    except Exception:
        return None
