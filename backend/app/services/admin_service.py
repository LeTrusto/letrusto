from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.entities import AnalyticsEvent, Deal, Notification, Product, SupportTicket, User
from app.repositories.user_repository import UserRepository
from app.schemas.admin import AdminDashboardStats, AdminUserDTO, AdminUserListResponse


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    def get_dashboard_stats(self) -> AdminDashboardStats:
        from app.models.entities import Category
        return AdminDashboardStats(
            total_users=self.db.query(User).count(),
            total_products=self.db.query(Product).count(),
            total_categories=self.db.query(Category).count(),
            total_deals=self.db.query(Deal).count(),
            total_support_tickets=self.db.query(SupportTicket).count(),
            open_support_tickets=self.db.query(SupportTicket).filter(SupportTicket.status == "open").count(),
            total_analytics_events=self.db.query(AnalyticsEvent).count(),
            total_notifications_sent=self.db.query(Notification).count(),
        )

    def list_users(self, skip: int = 0, limit: int = 50) -> AdminUserListResponse:
        users, total = self.user_repo.list_all(skip=skip, limit=limit)
        dtos = [
            AdminUserDTO(
                id=str(u.id),
                email=u.email,
                full_name=u.full_name,
                role=u.role,
                is_active=u.is_active,
                email_verified=u.email_verified,
                created_at=u.created_at.isoformat(),
            )
            for u in users
        ]
        return AdminUserListResponse(users=dtos, total=total)
