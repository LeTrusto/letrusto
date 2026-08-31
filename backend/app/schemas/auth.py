from pydantic import BaseModel, EmailStr, Field


class TokenRequest(BaseModel):
    subject: str = Field(min_length=3, max_length=80)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenIntrospectionResponse(BaseModel):
    subject: str
    expiresAt: int


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    full_name: str = Field(min_length=1, max_length=200)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=64)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=20, max_length=255)
    password: str = Field(min_length=8, max_length=64)


class EmailVerificationConfirm(BaseModel):
    token: str = Field(min_length=20, max_length=255)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=10)


class OtpRequest(BaseModel):
    mobile_number: str = Field(min_length=10, max_length=16)


class OtpVerifyRequest(BaseModel):
    mobile_number: str = Field(min_length=10, max_length=16)
    otp: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")


class OtpRequestResponse(BaseModel):
    message: str


class LinkEmailRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    email: str | None
    full_name: str
    role: str
    avatar_url: str | None
