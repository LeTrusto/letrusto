import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import _build_cors_origins, app


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


def test_production_allows_unconfigured_razorpay(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://db.example.invalid/letrusto")
    monkeypatch.setenv("JWT_SECRET_KEY", "12345678901234567890123456789012")
    monkeypatch.setenv("CASHFREE_ENV", "production")
    monkeypatch.setenv("RESEND_API_KEY", "test-resend-key")
    monkeypatch.setenv("RAZORPAY_ENV", "sandbox")
    monkeypatch.delenv("RAZORPAY_KEY_ID", raising=False)
    monkeypatch.delenv("RAZORPAY_KEY_SECRET", raising=False)
    monkeypatch.delenv("RAZORPAY_WEBHOOK_SECRET", raising=False)
    get_settings.cache_clear()
    try:
        settings = get_settings()
        assert settings.RAZORPAY_KEY_ID == ""
        assert settings.RAZORPAY_KEY_SECRET == ""
        assert settings.RAZORPAY_WEBHOOK_SECRET == ""
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


def test_production_cors_filters_localhost_and_wildcard():
    origins = _build_cors_origins("*, http://localhost:3000, https://shop.example.com", "production")
    assert "*" not in origins
    assert "http://localhost:3000" not in origins
    assert "https://shop.example.com" in origins


def test_production_requires_razorpay_webhook_secret_when_credentials_are_configured(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://db.example.invalid/letrusto")
    monkeypatch.setenv("JWT_SECRET_KEY", "12345678901234567890123456789012")
    monkeypatch.setenv("CASHFREE_ENV", "production")
    monkeypatch.setenv("RESEND_API_KEY", "test-resend-key")
    monkeypatch.setenv("RAZORPAY_KEY_ID", "rzp_test_configured")
    monkeypatch.setenv("RAZORPAY_KEY_SECRET", "configured-secret")
    monkeypatch.delenv("RAZORPAY_WEBHOOK_SECRET", raising=False)
    get_settings.cache_clear()
    try:
        with pytest.raises(RuntimeError, match="RAZORPAY_WEBHOOK_SECRET"):
            get_settings()
    finally:
        get_settings.cache_clear()
