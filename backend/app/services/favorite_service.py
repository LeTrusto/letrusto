import uuid

from app.core.exceptions import NotFoundError
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.favorite import FavoriteListResponse
from app.services.product_mapper import to_product_dto


class FavoriteService:
    def __init__(self, favorite_repository: FavoriteRepository, product_repository: ProductRepository) -> None:
        self.favorite_repository = favorite_repository
        self.product_repository = product_repository

    def list_favorites(self, user_id: uuid.UUID) -> FavoriteListResponse:
        slugs = self.favorite_repository.list_product_slugs(user_id)
        products = self.product_repository.list_products(slugs)
        ordered = sorted(products, key=lambda item: slugs.index(item.slug) if item.slug in slugs else 10_000)

        return FavoriteListResponse(
            userId=user_id,
            items=[to_product_dto(product, self.product_repository.get_similar_slugs(product.id)) for product in ordered],
        )

    def add_favorite(self, user_id: uuid.UUID, product_slug: str) -> None:
        product = self.product_repository.get_by_slug(product_slug)
        if not product:
            raise NotFoundError(f"Product '{product_slug}' not found")
        self.favorite_repository.add(user_id, product.id)

    def remove_favorite(self, user_id: uuid.UUID, product_slug: str) -> bool:
        product = self.product_repository.get_by_slug(product_slug)
        if not product:
            raise NotFoundError(f"Product '{product_slug}' not found")
        return self.favorite_repository.remove(user_id, product.id)
