from fastapi import APIRouter

from app.core.config import get_settings
from app.api.v1.endpoints import (
    account,
    auth,
    health,
)

api_router = APIRouter()
settings = get_settings()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(account.router)

