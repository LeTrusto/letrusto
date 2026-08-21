import uuid

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.ai.providers.factory import build_llm_provider
from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError
from app.db.session import SessionLocal, get_db  # noqa: F401 — re-exported for endpoints
from app.models.entities import User
from app.repositories.ai_tool_repository import AIToolRepository
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.product_repository import ProductRepository
from app.services.email_service import EmailService
from app.services.admin_service import AdminService
from app.services.admin_product_service import AdminProductService
from app.services.ai_service import AIService, InMemorySessionStore
from app.services.ai_tool_intent_router import AIToolIntentRouter
from app.services.ai_tool_recommendation_service import AIToolRecommendationService
from app.services.ai_tool_service import AIToolService
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import AuthService
from app.services.deal_service import DealService
from app.services.favorite_service import FavoriteService
from app.services.notification_service import NotificationService
from app.services.order_service import OrderService
from app.services.cashfree_service import CashfreeService
from app.services.razorpay_service import RazorpayService
from app.services.fulfillment_service import FulfillmentService
from app.services.fulfillment_preflight_service import FulfillmentPreflightService
from app.services.product_service import ProductService
from app.services.support_service import SupportService
from app.services.user_service import UserService


settings = get_settings()
session_store = InMemorySessionStore(ttl_minutes=settings.AI_SESSION_TTL_MINUTES)
llm_provider = build_llm_provider(settings.AI_PROVIDER)
ai_tool_intent_router = AIToolIntentRouter()


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(ProductRepository(db))


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    return OrderService(db)


def get_cashfree_service(db: Session = Depends(get_db)) -> CashfreeService:
    return CashfreeService(db)


def get_razorpay_service(db: Session = Depends(get_db)) -> RazorpayService:
    return RazorpayService(db)


def get_cancellation_service(db: Session = Depends(get_db)) -> "CancellationService":
    from app.services.cancellation_service import CancellationService
    return CancellationService(db, cashfree_service=CashfreeService(db))


def get_fulfillment_service(db: Session = Depends(get_db)) -> FulfillmentService:
    return FulfillmentService(db)


def get_fulfillment_preflight_service(db: Session = Depends(get_db)) -> FulfillmentPreflightService:
    return FulfillmentPreflightService(db)


def get_favorite_service(db: Session = Depends(get_db)) -> FavoriteService:
    return FavoriteService(FavoriteRepository(db), ProductRepository(db))


def get_ai_service(db: Session = Depends(get_db)) -> AIService:
    return AIService(
        ProductRepository(db),
        llm_provider,
        session_store,
        ai_tool_intent_router=ai_tool_intent_router,
        ai_tool_recommendation_service=AIToolRecommendationService(AIToolRepository(db)),
    )


def get_ai_tool_service(db: Session = Depends(get_db)) -> AIToolService:
    return AIToolService(AIToolRepository(db), intent_router=ai_tool_intent_router)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


def get_deal_service(db: Session = Depends(get_db)) -> DealService:
    return DealService(db)


def get_support_service(db: Session = Depends(get_db)) -> SupportService:
    return SupportService(db, email_service=get_email_service())


def get_email_service() -> EmailService:
    return EmailService.from_settings(settings)


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(db)


def get_admin_product_service(db: Session = Depends(get_db)) -> AdminProductService:
    return AdminProductService(db)


def _extract_bearer(authorization: str) -> str:
    if not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise UnauthorizedError("Missing bearer token")
    return token


def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User:
    token = _extract_bearer(authorization)
    return AuthService(db).get_current_user(token)


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise UnauthorizedError("Admin access required")
    return current_user


def get_optional_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User | None:
    if not authorization:
        return None
    try:
        token = _extract_bearer(authorization)
        return AuthService(db).get_current_user(token)
    except Exception:
        return None
