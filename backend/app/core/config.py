from decimal import Decimal
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

    APP_NAME: str = "LeTrusto Backend"
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

    AI_PROVIDER: str = "heuristic"
    AI_SESSION_TTL_MINUTES: int = 120

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    INVENTORY_RESERVATION_TTL_MINUTES: int = 15
    PENDING_PAYMENT_RECONCILIATION_AGE_MINUTES: int = 30
    RECONCILIATION_BATCH_SIZE: int = 50
    ORDER_RECONCILIATION_ENABLED: bool = True

    # Supplier integration (Phase 2 validation)
    SUPPLIER_PROVIDER: str = "cj"
    CJ_API_KEY: str = ""

    # Approved Phase 3.3.3 prepaid launch pricing policy
    PRICING_FX_RATE: Decimal = Decimal("98.00")
    PAYMENT_GATEWAY_PCT: Decimal = Decimal("2.36")
    RTO_RESERVE_PCT: Decimal = Decimal("4.00")
    TARGET_CONTRIBUTION_MARGIN_PCT: Decimal = Decimal("20.00")
    TARGET_CAC_INR: Decimal = Decimal("150.00")
    # Business configuration only; this does not assert legal GST exemption.
    CATALOG_TAX_TREATMENT: str = "UNREGISTERED_NO_GSTIN"
    CATALOG_TAX_RATE_PCT: Decimal | None = None

    # Cashfree Payments. Keep sandbox as the only default; production must be explicit.
    CASHFREE_ENV: str = "sandbox"
    CASHFREE_APP_ID: str = ""
    CASHFREE_SECRET_KEY: str = ""
    CASHFREE_WEBHOOK_SECRET: str = ""
    CASHFREE_API_VERSION: str = "2026-01-01"
    CASHFREE_RETURN_URL: str = "http://localhost:3000/orders/{order_id}"
    CASHFREE_NOTIFY_URL: str = "http://localhost:8000/api/v1/payments/cashfree/webhook"

    # Rate limiting (requests per minute per IP)
    RATE_LIMIT_AUTH: int = 10
    RATE_LIMIT_DEFAULT: int = 120


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
    if s.CASHFREE_ENV not in {"sandbox", "production"}:
        raise ValueError("CASHFREE_ENV must be sandbox or production")
    if s.APP_ENV == "production" and s.CASHFREE_ENV != "production":
        raise RuntimeError("Production app requires CASHFREE_ENV=production")
    return s
