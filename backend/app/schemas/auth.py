from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    subject: str = Field(min_length=3, max_length=80)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenIntrospectionResponse(BaseModel):
    subject: str
    expiresAt: int
