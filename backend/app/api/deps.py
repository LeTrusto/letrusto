from fastapi import Depends
from sqlalchemy.orm import Session

from app.ai.providers.factory import build_llm_provider
from app.core.config import get_settings
from app.db.session import get_db
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.product_repository import ProductRepository
from app.services.ai_service import AIService, InMemorySessionStore
from app.services.auth_service import AuthService
from app.services.favorite_service import FavoriteService
from app.services.product_service import ProductService


settings = get_settings()
session_store = InMemorySessionStore(ttl_minutes=settings.AI_SESSION_TTL_MINUTES)
llm_provider = build_llm_provider(settings.AI_PROVIDER)


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(ProductRepository(db))


def get_favorite_service(db: Session = Depends(get_db)) -> FavoriteService:
    return FavoriteService(FavoriteRepository(db), ProductRepository(db))


def get_ai_service(db: Session = Depends(get_db)) -> AIService:
    return AIService(ProductRepository(db), llm_provider, session_store)


def get_auth_service() -> AuthService:
    return AuthService()
