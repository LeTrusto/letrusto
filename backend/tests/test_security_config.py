import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


def test_production_rejects_default_jwt_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://db.example.invalid/letrusto")
    monkeypatch.setenv("JWT_SECRET_KEY", "change-this-secret-for-production")
    monkeypatch.setenv("CASHFREE_ENV", "production")
    get_settings.cache_clear()
    try:
        with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
            get_settings()
    finally:
        get_settings.cache_clear()


def test_credentialed_cors_allows_only_configured_origins():
    client = TestClient(app)
    allowed = client.options(
        "/api/v1/products",
        headers={"Origin": "https://letrusto.com", "Access-Control-Request-Method": "GET"},
    )
    blocked = client.options(
        "/api/v1/products",
        headers={"Origin": "https://untrusted.vercel.app", "Access-Control-Request-Method": "GET"},
    )
    assert allowed.headers["access-control-allow-origin"] == "https://letrusto.com"
    assert "access-control-allow-origin" not in blocked.headers
