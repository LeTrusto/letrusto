from app.core.config import get_settings
from app.core.security import create_access_token, decode_token
from app.schemas.auth import TokenIntrospectionResponse, TokenResponse


class AuthService:
    def issue_token(self, subject: str) -> TokenResponse:
        settings = get_settings()
        token = create_access_token(subject=subject)
        return TokenResponse(
            access_token=token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def introspect(self, token: str) -> TokenIntrospectionResponse:
        payload = decode_token(token)
        subject = payload.get("sub", "")
        exp = int(payload.get("exp", 0))
        return TokenIntrospectionResponse(subject=subject, expiresAt=exp)
