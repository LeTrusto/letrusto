from __future__ import annotations

import json
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.entities import Notification, PriceAlert, SavedComparison, User
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    DashboardResponse,
    PriceAlertCreateRequest,
    PriceAlertDTO,
    SavedComparisonCreateRequest,
    SavedComparisonDTO,
    UserDTO,
    UserProfileUpdateRequest,
)
from app.services.otp_auth_service import normalize_indian_mobile


def _to_user_dto(user) -> UserDTO:
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
        self.product_repo = ProductRepository(db)

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

    # ── Saved Comparisons ────────────────────────────────────────────────────
    def list_saved_comparisons(self, user_id: uuid.UUID) -> list[SavedComparisonDTO]:
        rows = self.db.query(SavedComparison).filter(SavedComparison.user_id == user_id).all()
        return [SavedComparisonDTO(
            id=r.id,
            product_ids=json.loads(r.product_ids),
            label=r.label,
            created_at=r.created_at.isoformat(),
        ) for r in rows]

    def save_comparison(self, user_id: uuid.UUID, req: SavedComparisonCreateRequest) -> SavedComparisonDTO:
        row = SavedComparison(
            user_id=user_id,
            product_ids=json.dumps(req.product_ids),
            label=req.label,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return SavedComparisonDTO(
            id=row.id,
            product_ids=json.loads(row.product_ids),
            label=row.label,
            created_at=row.created_at.isoformat(),
        )

    def delete_saved_comparison(self, user_id: uuid.UUID, comparison_id: int) -> None:
        row = self.db.query(SavedComparison).filter(
            SavedComparison.id == comparison_id, SavedComparison.user_id == user_id
        ).first()
        if row:
            self.db.delete(row)
            self.db.commit()

    # ── Price Alerts ─────────────────────────────────────────────────────────
    def list_price_alerts(self, user_id: uuid.UUID) -> list[PriceAlertDTO]:
        rows = self.db.query(PriceAlert).filter(PriceAlert.user_id == user_id).all()
        result = []
        for r in rows:
            product = self.product_repo.get_by_id(r.product_id)
            result.append(PriceAlertDTO(
                id=r.id,
                product_id=str(r.product_id),
                product_name=product.name if product else "Unknown",
                current_price=float(product.price_value) if product else 0,
                target_price=float(r.target_price) if r.target_price else None,
                is_active=r.is_active,
                created_at=r.created_at.isoformat(),
            ))
        return result

    def create_price_alert(self, user_id: uuid.UUID, req: PriceAlertCreateRequest) -> PriceAlertDTO:
        try:
            product_id = uuid.UUID(req.product_id)
        except ValueError as exc:
            raise BadRequestError("Invalid product ID") from exc
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product not found")
        existing = self.db.query(PriceAlert).filter(
            PriceAlert.user_id == user_id, PriceAlert.product_id == product_id
        ).first()
        if existing:
            raise BadRequestError("Price alert already exists for this product")
        alert = PriceAlert(user_id=user_id, product_id=product_id, target_price=req.target_price)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return PriceAlertDTO(
            id=alert.id,
            product_id=str(alert.product_id),
            product_name=product.name,
            current_price=float(product.price_value),
            target_price=float(alert.target_price) if alert.target_price else None,
            is_active=alert.is_active,
            created_at=alert.created_at.isoformat(),
        )

    def delete_price_alert(self, user_id: uuid.UUID, alert_id: int) -> None:
        row = self.db.query(PriceAlert).filter(
            PriceAlert.id == alert_id, PriceAlert.user_id == user_id
        ).first()
        if row:
            self.db.delete(row)
            self.db.commit()

    # ── Dashboard ────────────────────────────────────────────────────────────
    def get_dashboard(self, user_id: uuid.UUID) -> DashboardResponse:
        from app.models.entities import AiConversation, Favorite
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        favorites_count = self.db.query(Favorite).filter(Favorite.user_id == user_id).count()
        saved_comparisons = self.list_saved_comparisons(user_id)
        price_alerts = self.list_price_alerts(user_id)
        unread_notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id, Notification.is_read.is_(False)
        ).count()
        recent_conversations_count = self.db.query(AiConversation).filter(
            AiConversation.user_id == user_id
        ).count()
        return DashboardResponse(
            user=_to_user_dto(user),
            favorites_count=favorites_count,
            saved_comparisons=saved_comparisons,
            price_alerts=price_alerts,
            unread_notifications=unread_notifications,
            recent_conversations_count=recent_conversations_count,
        )
