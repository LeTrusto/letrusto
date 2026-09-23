from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.core.exceptions import NotFoundError
from app.models.entities import MonetizationPlan, User
from app.schemas.admin import MonetizationPlanDTO, MonetizationPlanUpdate


router = APIRouter(prefix="/admin/monetization", tags=["admin-monetization"])


@router.get("/plans", response_model=list[MonetizationPlanDTO])
def list_plans(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.scalars(select(MonetizationPlan).order_by(MonetizationPlan.sort_order, MonetizationPlan.code)).all()


@router.patch("/plans/{code}", response_model=MonetizationPlanDTO)
def update_plan(code: str, payload: MonetizationPlanUpdate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    plan = db.scalar(select(MonetizationPlan).where(MonetizationPlan.code == code.upper()))
    if not plan:
        raise NotFoundError("Monetization plan not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    plan.customer_purchase_enabled = False
    db.commit()
    db.refresh(plan)
    return plan