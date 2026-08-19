import os
import sys
from collections import OrderedDict

# Report connection configuration without exposing credentials in deployment logs.
_database_url_configured = bool(os.environ.get("DATABASE_URL"))
print(f"[LeTrusto BOOT] sys.version={sys.version}", flush=True)
print(
    f"[LeTrusto BOOT] DATABASE_URL configured={_database_url_configured}",
    flush=True,
)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.rate_limit import RateLimitMiddleware
from app.core.security import TokenPayloadError

settings = get_settings()

def _build_cors_origins(raw_origins: str) -> list[str]:
    configured = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    defaults = [
        "https://letrusto.com",
        "https://www.letrusto.com",
        "https://letrusto.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Keep order stable while removing duplicates.
    return list(OrderedDict.fromkeys([*configured, *defaults]))


_cors_origins = _build_cors_origins(settings.CORS_ORIGINS)

print(f"[LeTrusto] APP_ENV={settings.APP_ENV}")
print(f"[LeTrusto] DATABASE_URL configured={bool(settings.DATABASE_URL)}")
print(f"[LeTrusto] CORS_ORIGINS={settings.CORS_ORIGINS}")
print(f"[LeTrusto] Effective CORS origins={_cors_origins}")

app = FastAPI(
    title=settings.APP_NAME,
    version="5.0.0",
    openapi_url="/openapi.json" if settings.APP_ENV != "production" else None,
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    RateLimitMiddleware,
    default_limit=0 if settings.APP_ENV == "development" else settings.RATE_LIMIT_DEFAULT,
    auth_limit=settings.RATE_LIMIT_AUTH,
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Print routes at module load time (not as startup event — avoids uvicorn startup hang)
_routes = sorted(
    [f"{sorted(r.methods)[0]} {r.path}" for r in app.routes if hasattr(r, "methods") and r.methods],
    key=lambda x: x.split(" ", 1)[1],
)
print(f"[LeTrusto] {len(_routes)} routes registered", flush=True)


@app.get("/", include_in_schema=False)
def root() -> dict:
    return {
        "service": "LeTrusto Backend API",
        "status": "running",
        "docs": "/docs",
        "api_prefix": settings.API_V1_PREFIX,
        "note": "All endpoints are under /api/v1 — e.g. /api/v1/products/metadata",
    }


@app.exception_handler(TokenPayloadError)
async def token_payload_error_handler(_: Request, exc: TokenPayloadError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})
