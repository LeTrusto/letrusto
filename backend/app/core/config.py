from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


_BACKEND_DIR = Path(__file__).resolve().parents[2]
_ENV_FILE = _BACKEND_DIR / ".env"


def _normalise_db_url(url: str) -> str:
    """Ensure the pg8000 driver is used regardless of how Railway injects DATABASE_URL."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+pg8000://", 1)
    elif url.startswith("postgresql://") and "+pg8000" not in url:
        url = url.replace("postgresql://", "postgresql+pg8000://", 1)
    return url


class Settings(BaseSettings):
    # env_file is only read when .env exists; real env vars always take precedence
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Bangalore Property Platform"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+pg8000://postgres:postgres@localhost:5432/letrusto"

    JWT_SECRET_KEY: str = "change-this-secret-for-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: str = "http://localhost:3000"

    RESEND_API_KEY: str = ""
    SUPPORT_EMAIL: str = "hello@letrusto.com"
    FROM_EMAIL: str = "support@letrusto.com"
    PUBLIC_APP_URL: str = "https://letrusto.com"

    SMS_PROVIDER: str = "mock"
    SMS_API_URL: str = ""
    SMS_API_KEY: str = ""
    SMS_SENDER_ID: str = ""
    OTP_EXPIRE_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RESEND_COOLDOWN_SECONDS: int = 60
    OTP_MAX_REQUESTS_PER_HOUR: int = 5

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Rate limiting (requests per minute per IP)
    RATE_LIMIT_AUTH: int = 10
    RATE_LIMIT_DEFAULT: int = 120

    STORAGE_PROVIDER: str = "mock"
    STORAGE_ENDPOINT: str = ""
    STORAGE_REGION: str = "auto"
    STORAGE_BUCKET: str = ""
    STORAGE_ACCESS_KEY: str = ""
    STORAGE_SECRET_KEY: str = ""
    STORAGE_PUBLIC_BASE_URL: str = ""
    STORAGE_UPLOAD_EXPIRE_SECONDS: int = 600
    IMAGE_MAX_SIZE_MB: int = 10
    VIDEO_MAX_SIZE_MB: int = 100


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.DATABASE_URL = _normalise_db_url(s.DATABASE_URL)

    # Only fail loudly in production — localhost is valid for local development
    if s.APP_ENV == "production" and ("localhost" in s.DATABASE_URL or "127.0.0.1" in s.DATABASE_URL):
        raise RuntimeError(
            f"\n\n"
            f"=================================================================\n"
            f"FATAL: DATABASE_URL is pointing to localhost.\n"
            f"  DATABASE_URL is configured but resolves to a local host.\n"
            f"\n"
            f"  Fix: In Railway → your service → Variables, add:\n"
            f"    DATABASE_URL = (copy from the PostgreSQL service plugin)\n"
            f"=================================================================\n"
        )
    if s.APP_ENV == "production" and (
        s.JWT_SECRET_KEY.startswith("change-this-") or len(s.JWT_SECRET_KEY) < 32
    ):
        raise RuntimeError("FATAL: JWT_SECRET_KEY must be a non-placeholder value of at least 32 characters in production.")
    if s.APP_ENV == "production" and (
        not s.RESEND_API_KEY
        or not s.PUBLIC_APP_URL.startswith("https://")
        or "localhost" in s.PUBLIC_APP_URL.lower()
        or "127.0.0.1" in s.PUBLIC_APP_URL
    ):
        raise RuntimeError("FATAL: production email delivery requires RESEND_API_KEY and a non-local HTTPS PUBLIC_APP_URL.")
    return s
