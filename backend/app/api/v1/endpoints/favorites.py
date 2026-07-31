from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_favorite_service
from app.schemas.common import MessageResponse
from app.schemas.favorite import FavoriteListResponse
from app.services.favorite_service import FavoriteService

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=FavoriteListResponse)
def list_favorites(
    userId: UUID = Query(...),
    service: FavoriteService = Depends(get_favorite_service),
) -> FavoriteListResponse:
    return service.list_favorites(userId)


@router.post("/{product_id}", response_model=MessageResponse)
def add_favorite(
    product_id: str,
    userId: UUID = Query(...),
    service: FavoriteService = Depends(get_favorite_service),
) -> MessageResponse:
    service.add_favorite(userId, product_id)
    return MessageResponse(message="Favorite added")


@router.delete("/{product_id}", response_model=MessageResponse)
def remove_favorite(
    product_id: str,
    userId: UUID = Query(...),
    service: FavoriteService = Depends(get_favorite_service),
) -> MessageResponse:
    removed = service.remove_favorite(userId, product_id)
    return MessageResponse(message="Favorite removed" if removed else "Favorite did not exist")
