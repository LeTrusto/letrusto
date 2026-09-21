from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.entities import SellerProfile, User
from app.schemas.seller import SellerProfileRequest, SellerProfileUpdate


class SellerProfileService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_or_create(self, user: User, payload: SellerProfileRequest | None = None) -> SellerProfile:
        profile = self.db.scalar(select(SellerProfile).where(SellerProfile.user_id == user.id))
        if profile:
            return profile
        if payload is None:
            raise NotFoundError("Seller profile not found")
        profile = SellerProfile(user_id=user.id, **payload.model_dump())
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(self, user: User, payload: SellerProfileUpdate) -> SellerProfile:
        profile = self.get_or_create(user)
        if profile.user_id != user.id:
            raise NotFoundError("Seller profile not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
        self.db.commit()
        self.db.refresh(profile)
        return profile
