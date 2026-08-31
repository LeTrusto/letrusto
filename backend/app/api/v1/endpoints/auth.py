from fastapi import APIRouter, Depends, Header

from app.api.deps import get_auth_service, get_current_user
from app.core.exceptions import UnauthorizedError
from app.models.entities import User
from app.schemas.auth import (
    AuthResponse,
    EmailVerificationConfirm,
    LinkEmailRequest,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    TokenIntrospectionResponse,
    TokenRequest,
    TokenResponse,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.core.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


def _send_verification_email(service: AuthService, user: User) -> None:
    settings = get_settings()
    if not settings.RESEND_API_KEY or not user.email:
        return
    token = service.create_email_verification_token(user)
    verification_url = f"{settings.PUBLIC_APP_URL.rstrip('/')}/verify-email?token={token}"
    EmailService.from_settings(settings)._send(
        to=user.email,
        subject="Verify your LeTrusto email",
        html=f"<p>Welcome to LeTrusto.</p><p><a href='{verification_url}'>Verify your email address</a></p><p>This link expires in 30 minutes.</p>",
        text=f"Verify your LeTrusto email: {verification_url}\nThis link expires in 30 minutes.",
        template_name="email_verification",
    )


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(payload: RegisterRequest, service: AuthService = Depends(get_auth_service)) -> AuthResponse:
    response = service.register(email=payload.email, password=payload.password, full_name=payload.full_name)
    user = service.user_repo.get_by_id(response.user_id)
    if user:
        _send_verification_email(service, user)
    return response


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)) -> AuthResponse:
    return service.login(email=payload.email, password=payload.password)


@router.post("/password-reset/request", response_model=MessageResponse)
def request_password_reset(payload: PasswordResetRequest, service: AuthService = Depends(get_auth_service)) -> MessageResponse:
    result = service.create_password_reset_token(str(payload.email))
    if result:
        token, email = result
        reset_url = f"{get_settings().PUBLIC_APP_URL.rstrip('/')}/reset-password?token={token}"
        EmailService.from_settings(get_settings())._send(
            to=email,
            subject="Reset your LeTrusto password",
            html=f"<p>We received a request to reset your LeTrusto password.</p><p><a href='{reset_url}'>Reset your password</a></p><p>This link expires in 30 minutes.</p>",
            text=f"Reset your LeTrusto password: {reset_url}\nThis link expires in 30 minutes.",
            template_name="password_reset",
        )
    return MessageResponse(message="If an account exists for that email, a reset link has been sent.")


@router.post("/email-verification/resend", response_model=MessageResponse)
def resend_email_verification(payload: PasswordResetRequest, service: AuthService = Depends(get_auth_service)) -> MessageResponse:
    user = service.user_repo.get_by_email(str(payload.email).strip().lower())
    if user and not user.email_verified:
        _send_verification_email(service, user)
    return MessageResponse(message="If an unverified account exists for that email, a verification link has been sent.")


@router.post("/password-reset/confirm", response_model=MessageResponse)
def confirm_password_reset(payload: PasswordResetConfirm, service: AuthService = Depends(get_auth_service)) -> MessageResponse:
    service.reset_password(payload.token, payload.password)
    return MessageResponse(message="Your password has been reset. You can now sign in.")


@router.post("/email-verification/confirm", response_model=MessageResponse)
def confirm_email_verification(payload: EmailVerificationConfirm, service: AuthService = Depends(get_auth_service)) -> MessageResponse:
    service.verify_email(payload.token)
    return MessageResponse(message="Your email has been verified.")


@router.post("/link-email", response_model=AuthResponse)
def link_email(
    payload: LinkEmailRequest,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    if current_user.role != "user":
        raise UnauthorizedError("Customer authentication required")
    return service.link_email(current_user, str(payload.email), payload.password)


@router.post("/refresh", response_model=AuthResponse)
def refresh_token(payload: RefreshRequest, service: AuthService = Depends(get_auth_service)) -> AuthResponse:
    return service.refresh(payload.refresh_token)


@router.post("/logout", response_model=MessageResponse)
def logout(payload: RefreshRequest, service: AuthService = Depends(get_auth_service)) -> MessageResponse:
    service.logout(payload.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=TokenIntrospectionResponse)
def get_me(
    authorization: str = Header(default=""),
    service: AuthService = Depends(get_auth_service),
) -> TokenIntrospectionResponse:
    if not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise UnauthorizedError("Missing bearer token")
    return service.introspect(token)


# Legacy token endpoint retained for internal/test use
@router.post("/token", response_model=TokenResponse)
def issue_token(payload: TokenRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    return service.issue_token(payload.subject)
