import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalise_db_url(url: str) -> str:
    """Ensure the pg8000 driver is used regardless of how Railway injects DATABASE_URL."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+pg8000://", 1)
    elif url.startswith("postgresql://") and "+pg8000" not in url:
        url = url.replace("postgresql://", "postgresql+pg8000://", 1)
    return url


class Settings(BaseSettings):
    # env_file is only read when .env exists; real env vars always take precedence
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

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

    # Rate limiting (requests per minute per IP)
    RATE_LIMIT_AUTH: int = 10
    RATE_LIMIT_DEFAULT: int = 120


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.DATABASE_URL = _normalise_db_url(s.DATABASE_URL)

    # Only fail loudly in production — localhost is valid for local development
    if s.APP_ENV == "production" and ("localhost" in s.DATABASE_URL or "127.0.0.1" in s.DATABASE_URL):
        env_val = os.environ.get("DATABASE_URL", "<not set>")
        raise RuntimeError(
            f"\n\n"
            f"=================================================================\n"
            f"FATAL: DATABASE_URL is pointing to localhost.\n"
            f"  Env var DATABASE_URL = {env_val}\n"
            f"  Resolved DATABASE_URL = {s.DATABASE_URL}\n"
            f"\n"
            f"  Fix: In Railway → your service → Variables, add:\n"
            f"    DATABASE_URL = (copy from the PostgreSQL service plugin)\n"
            f"=================================================================\n"
        )
    return s
