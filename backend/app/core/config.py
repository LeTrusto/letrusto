from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "LeTrusto Backend"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+pg8000://postgres:postgres@localhost:5432/letrusto"

    JWT_SECRET_KEY: str = "change-this-secret-for-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    CORS_ORIGINS: str = "http://localhost:3000"

    AI_PROVIDER: str = "heuristic"
    AI_SESSION_TTL_MINUTES: int = 120


@lru_cache
def get_settings() -> Settings:
    return Settings()
