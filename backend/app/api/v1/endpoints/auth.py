from fastapi import APIRouter, Depends, Header, Request

from app.api.deps import get_auth_service, get_current_user
from app.core.exceptions import UnauthorizedError
from app.models.entities import User
from app.schemas.auth import (
    AuthResponse,
    LinkEmailRequest,
    LoginRequest,
    OtpRequest,
    OtpRequestResponse,
    OtpVerifyRequest,
    RefreshRequest,
    RegisterRequest,
    TokenIntrospectionResponse,
    TokenRequest,
    TokenResponse,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService
from app.services.otp_auth_service import OtpAuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(payload: RegisterRequest, service: AuthService = Depends(get_auth_service)) -> AuthResponse:
    return service.register(email=payload.email, password=payload.password, full_name=payload.full_name)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)) -> AuthResponse:
    return service.login(email=payload.email, password=payload.password)


@router.post("/otp/request", response_model=OtpRequestResponse)
def request_otp(payload: OtpRequest, request: Request, service: AuthService = Depends(get_auth_service)) -> OtpRequestResponse:
    OtpAuthService(service.db).request_otp(payload.mobile_number, request.client.host if request.client else None)
    return OtpRequestResponse(message="If this mobile number can receive messages, an OTP has been sent")


@router.post("/otp/verify", response_model=AuthResponse)
def verify_otp(payload: OtpVerifyRequest, service: AuthService = Depends(get_auth_service)) -> AuthResponse:
    return OtpAuthService(service.db).verify_otp(payload.mobile_number, payload.otp)


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
