import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.entities import Favorite
from app.models.entities import Product


class FavoriteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_product_slugs(self, user_id: uuid.UUID) -> list[str]:
        stmt = (
            select(Product.slug)
            .join(Favorite, Favorite.product_id == Product.id)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def add(self, user_id: uuid.UUID, product_id: uuid.UUID) -> None:
        exists = self.db.scalar(
            select(Favorite.id).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
        )
        if exists:
            return

        self.db.add(Favorite(user_id=user_id, product_id=product_id))
        self.db.commit()

    def remove(self, user_id: uuid.UUID, product_id: uuid.UUID) -> bool:
        stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id)
        result = self.db.execute(stmt)
        self.db.commit()
        return bool(result.rowcount)
