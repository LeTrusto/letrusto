from fastapi import APIRouter

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
    support,
    trust,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(ai.router)
api_router.include_router(ai_tools.router)
api_router.include_router(search.router)
api_router.include_router(compare.router)
api_router.include_router(recommendations.router)
api_router.include_router(products.router)
api_router.include_router(trust.router)
api_router.include_router(categories.router)
api_router.include_router(favorites.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(notifications.router)
api_router.include_router(orders.router)
api_router.include_router(deals.router)
api_router.include_router(digital_products.router)
api_router.include_router(support.router)
api_router.include_router(analytics.router)
api_router.include_router(admin.router)
api_router.include_router(account.router)
api_router.include_router(affiliate.router)
api_router.include_router(articles.router)
api_router.include_router(supplier_discovery.router)
api_router.include_router(supplier_validation.router)
