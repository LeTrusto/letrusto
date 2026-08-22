from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.exceptions import BadRequestError, UnauthorizedError
from app.models.entities import OtpChallenge, RefreshToken, User
from app.services.auth_service import AuthService
from app.services.otp_auth_service import OtpAuthService, _hash_otp
from app.services.sms_provider import MockSmsProvider
from app.services.sms_provider import get_sms_provider


@pytest.fixture()
def db():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    for model in (User, RefreshToken, OtpChallenge):
        model.__table__.create(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def sms():
    MockSmsProvider.sent.clear()
    return MockSmsProvider()


def issue(db, sms, mobile="9876543210"):
    OtpAuthService(db, sms).request_otp(mobile)
    return MockSmsProvider.sent[-1].otp


def test_otp_request_does_not_return_code(db, sms, caplog):
    issue(db, sms)
    assert len(sms.sent) == 1
    assert len(sms.sent[0].otp) == 4
    assert db.query(OtpChallenge).one().code_hash != sms.sent[0].otp
    assert sms.sent[0].otp not in caplog.text


def test_otp_preserves_leading_zeroes(db, sms, monkeypatch):
    monkeypatch.setattr("app.services.otp_auth_service.secrets.randbelow", lambda _: 7)
    code = issue(db, sms)
    assert code == "0007"
    assert len(code) == 4


@pytest.mark.parametrize("invalid_otp", ["123", "12345", "123456"])
def test_invalid_otp_lengths_are_rejected_without_consuming_attempt(db, sms, invalid_otp):
    issue(db, sms)
    with pytest.raises(UnauthorizedError, match="Invalid or expired OTP"):
        OtpAuthService(db, sms).verify_otp("9876543210", invalid_otp)
    assert db.query(OtpChallenge).one().attempts == 0


def test_expired_otp_is_rejected(db, sms):
    issue(db, sms)
    challenge = db.query(OtpChallenge).one()
    challenge.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db.commit()
    with pytest.raises(UnauthorizedError, match="Invalid or expired OTP"):
        OtpAuthService(db, sms).verify_otp("9876543210", sms.sent[0].otp)


def test_wrong_otp_and_attempt_limit(db, sms):
    issue(db, sms)
    service = OtpAuthService(db, sms)
    for _ in range(5):
        with pytest.raises(UnauthorizedError):
            service.verify_otp("9876543210", "0000")
    with pytest.raises(UnauthorizedError, match="verification limit"):
        service.verify_otp("9876543210", sms.sent[0].otp)


def test_otp_replay_is_rejected(db, sms):
    code = issue(db, sms)
    service = OtpAuthService(db, sms)
    service.verify_otp("9876543210", code)
    with pytest.raises(UnauthorizedError):
        service.verify_otp("9876543210", code)


def test_resend_cooldown_and_hourly_rate_limit(db, sms):
    service = OtpAuthService(db, sms)
    issue(db, sms)
    with pytest.raises(BadRequestError, match="wait"):
        service.request_otp("9876543210")
    challenge = db.query(OtpChallenge).one()
    challenge.created_at = datetime.now(timezone.utc) - timedelta(seconds=61)
    db.commit()
    for _ in range(4):
        service.request_otp("9876543210")
        challenge = db.query(OtpChallenge).order_by(OtpChallenge.created_at.desc()).first()
        challenge.created_at = datetime.now(timezone.utc) - timedelta(seconds=61)
        db.commit()
    with pytest.raises(BadRequestError, match="Too many"):
        service.request_otp("9876543210")


def test_new_mobile_customer_is_created_and_tokens_are_issued(db, sms):
    code = issue(db, sms)
    response = OtpAuthService(db, sms).verify_otp("+91 98765 43210", code)
    user = db.query(User).one()
    assert user.mobile_number == "+919876543210"
    assert user.email is None
    assert response.user_id == str(user.id)
    assert response.access_token and response.refresh_token


def test_existing_mobile_customer_logs_into_same_account(db, sms):
    user = User(email="same@example.com", mobile_number="+919876543210", full_name="Same")
    db.add(user)
    db.commit()
    code = issue(db, sms)
    response = OtpAuthService(db, sms).verify_otp("9876543210", code)
    assert response.user_id == str(user.id)
    assert db.query(User).count() == 1


def test_email_and_mobile_login_share_account(db, sms):
    user = User(email="same@example.com", mobile_number="+919876543210", full_name="Same", password_hash="")
    db.add(user)
    db.commit()
    code = issue(db, sms)
    mobile_response = OtpAuthService(db, sms).verify_otp("9876543210", code)
    email_response = AuthService(db).link_email(user, "same@example.com", "correct-password")
    assert mobile_response.user_id == email_response.user_id == str(user.id)
    assert AuthService(db).login("same@example.com", "correct-password").user_id == str(user.id)


def test_duplicate_mobile_and_email_are_rejected(db, sms):
    user = User(email="one@example.com", mobile_number="+919876543210", full_name="One")
    db.add(user)
    db.commit()
    with pytest.raises(BadRequestError, match="already linked"):
        AuthService(db).link_email(user, "other@example.com", "correct-password")
    code = issue(db, sms)
    response = OtpAuthService(db, sms).verify_otp("9876543210", code)
    assert response.user_id == str(user.id)
    assert db.query(User).count() == 1


def test_explicit_account_linking_and_conflict_safety(db):
    user = User(full_name="Mobile")
    other = User(email="taken@example.com", full_name="Email")
    db.add_all([user, other])
    db.commit()
    user_response = AuthService(db).link_email(user, "new@example.com", "correct-password")
    assert user_response.email == "new@example.com"
    with pytest.raises(BadRequestError, match="another account"):
        AuthService(db).link_email(user, "taken@example.com", "correct-password")


def test_refresh_token_rotation_and_email_regression(db):
    user = User(email="login@example.com", full_name="Login", password_hash=None)
    db.add(user)
    db.commit()
    AuthService(db).link_email(user, "login@example.com", "correct-password")
    service = AuthService(db)
    response = service.login("login@example.com", "correct-password")
    refreshed = service.refresh(response.refresh_token)
    assert refreshed.refresh_token != response.refresh_token
    with pytest.raises(UnauthorizedError):
        service.refresh(response.refresh_token)


def test_admin_role_is_unchanged_by_customer_otp(db, sms):
    admin = User(email="admin@example.com", mobile_number="+919876543210", full_name="Admin", role="admin")
    db.add(admin)
    db.commit()
    code = issue(db, sms)
    with pytest.raises(UnauthorizedError):
        OtpAuthService(db, sms).verify_otp("9876543210", code)
    assert db.query(User).one().role == "admin"


def test_production_rejects_mock_sms_provider(monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("CASHFREE_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "12345678901234567890123456789012")
    monkeypatch.setenv("DATABASE_URL", "postgresql://db.example.invalid/letrusto")
    monkeypatch.setenv("SMS_PROVIDER", "mock")
    get_settings.cache_clear()
    try:
        with pytest.raises(BadRequestError, match="Production SMS"):
            get_sms_provider()
    finally:
        get_settings.cache_clear()
