from pydantic import BaseModel
from uuid import UUID

from app.schemas.product import ProductDTO


class FavoriteCreateRequest(BaseModel):
    userId: UUID
    productId: str


class FavoriteDeleteRequest(BaseModel):
    userId: UUID


class FavoriteListResponse(BaseModel):
    userId: UUID
    items: list[ProductDTO]
