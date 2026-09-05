from fastapi import APIRouter

from app.core.config import get_settings
from app.api.v1.endpoints import (
    admin,
    account,
    affiliate,
    ai,
    ai_tools,
    analytics,
    articles,
    auth,
    categories,
    compare,
    deals,
    digital_products,
    favorites,
    health,
    notifications,
    orders,
    products,
    recommendations,
    search,
    supplier_discovery,
    supplier_validation,
    subscriptions,
    support,
    trust,
    users,
    widget_events,
    widgets,
    public_embed,
    marketing,
)

api_router = APIRouter()
settings = get_settings()
api_router.include_router(health.router)
api_router.include_router(ai.router)
api_router.include_router(ai_tools.router)
api_router.include_router(search.router)
api_router.include_router(trust.router)
api_router.include_router(favorites.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(notifications.router)
api_router.include_router(digital_products.router)
api_router.include_router(support.router)
api_router.include_router(analytics.router)
api_router.include_router(account.router)
api_router.include_router(affiliate.router)
api_router.include_router(articles.router)
api_router.include_router(widgets.router)
api_router.include_router(widget_events.router)
api_router.include_router(public_embed.router)
api_router.include_router(subscriptions.router)
api_router.include_router(marketing.router)
if settings.PHYSICAL_COMMERCE_ENABLED:
    api_router.include_router(compare.router)
    api_router.include_router(recommendations.router)
    api_router.include_router(products.router)
    api_router.include_router(categories.router)
    api_router.include_router(orders.router)
    api_router.include_router(deals.router)
    api_router.include_router(admin.router)
    api_router.include_router(supplier_discovery.router)
    api_router.include_router(supplier_validation.router)

