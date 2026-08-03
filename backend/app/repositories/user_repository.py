from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.entities import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email.lower().strip()).first()

    def get_by_google_id(self, google_id: str) -> User | None:
        return self.db.query(User).filter(User.google_id == google_id).first()

    def create(self, email: str, full_name: str, password_hash: str | None = None, google_id: str | None = None) -> User:
        user = User(
            email=email.lower().strip(),
            full_name=full_name,
            password_hash=password_hash,
            google_id=google_id,
        )
        self.db.add(user)
        self.db.flush()
        return user

    def update_profile(self, user: User, full_name: str | None, avatar_url: str | None) -> User:
        if full_name is not None:
            user.full_name = full_name
        if avatar_url is not None:
            user.avatar_url = avatar_url
        self.db.flush()
        return user

    def list_all(self, skip: int = 0, limit: int = 50) -> tuple[list[User], int]:
        total = self.db.query(User).count()
        users = self.db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        return users, total
