from fastapi import APIRouter

from app.api.v1.endpoints import ai, auth, categories, compare, favorites, health, products, recommendations, search

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(ai.router)
api_router.include_router(search.router)
api_router.include_router(compare.router)
api_router.include_router(recommendations.router)
api_router.include_router(products.router)
api_router.include_router(categories.router)
api_router.include_router(favorites.router)
api_router.include_router(auth.router)
