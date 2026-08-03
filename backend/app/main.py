from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.rate_limit import RateLimitMiddleware
from app.core.security import TokenPayloadError

settings = get_settings()

# Mask password in logged URL for debugging Railway startup
_db_url_display = settings.DATABASE_URL
try:
    from urllib.parse import urlparse, urlunparse
    _p = urlparse(_db_url_display)
    if _p.password:
        _db_url_display = _db_url_display.replace(_p.password, "****")
except Exception:
    pass

print(f"[LeTrusto] APP_ENV={settings.APP_ENV}")
print(f"[LeTrusto] DATABASE_URL={_db_url_display}")
print(f"[LeTrusto] CORS_ORIGINS={settings.CORS_ORIGINS}")

app = FastAPI(
    title=settings.APP_NAME,
    version="5.0.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    RateLimitMiddleware,
    default_limit=settings.RATE_LIMIT_DEFAULT,
    auth_limit=settings.RATE_LIMIT_AUTH,
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.exception_handler(TokenPayloadError)
async def token_payload_error_handler(_: Request, exc: TokenPayloadError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})
