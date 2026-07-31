from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.product_repository import ProductRepository
from app.services.auth_service import AuthService
from app.services.favorite_service import FavoriteService
from app.services.product_service import ProductService


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(ProductRepository(db))


def get_favorite_service(db: Session = Depends(get_db)) -> FavoriteService:
    return FavoriteService(FavoriteRepository(db), ProductRepository(db))


def get_auth_service() -> AuthService:
    return AuthService()
