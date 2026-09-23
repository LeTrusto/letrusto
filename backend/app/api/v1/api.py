from fastapi import APIRouter

from app.core.config import get_settings
from app.api.v1.endpoints import (
    account,
    admin_properties,
    admin_campaigns,
    admin_monetization,
    auth,
    health,
    public_properties,
    notifications,
    seller_leads,
    seller_properties,
)

api_router = APIRouter()
settings = get_settings()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(account.router)
api_router.include_router(seller_properties.router)
api_router.include_router(seller_leads.router)
api_router.include_router(admin_properties.router)
api_router.include_router(admin_campaigns.router)
api_router.include_router(admin_monetization.router)
api_router.include_router(public_properties.router)
api_router.include_router(notifications.router)

