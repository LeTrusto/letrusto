from fastapi import APIRouter, Depends, Header

from app.api.deps import get_auth_service
from app.core.exceptions import UnauthorizedError
from app.schemas.auth import TokenIntrospectionResponse, TokenRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def issue_token(payload: TokenRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    return service.issue_token(payload.subject)


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
