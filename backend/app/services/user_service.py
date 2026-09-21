from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserDTO, UserProfileUpdateRequest
from app.models.entities import User
from app.services.otp_auth_service import normalize_indian_mobile


def _to_user_dto(user: User) -> UserDTO:
    return UserDTO(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active,
        email_verified=user.email_verified,
        created_at=user.created_at.isoformat(),
    )


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    def get_profile(self, user_id: uuid.UUID) -> UserDTO:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return _to_user_dto(user)

    def update_profile(self, user_id: uuid.UUID, req: UserProfileUpdateRequest) -> UserDTO:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        user = self.user_repo.update_profile(user, req.full_name, req.avatar_url)
        self.db.commit()
        self.db.refresh(user)
        return _to_user_dto(user)

    def update_customer_profile(self, user_id: uuid.UUID, full_name: str | None, phone: str | None, shipping_address) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        if full_name is not None:
            user.full_name = full_name
        if phone is not None:
            user.phone_number = normalize_indian_mobile(phone)
        if shipping_address is not None:
            user.shipping_address = shipping_address.model_dump()
        self.db.commit()
        self.db.refresh(user)
        return user
