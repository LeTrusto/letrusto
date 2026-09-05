from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import User, Widget
from app.schemas.widgets import WidgetCreate, WidgetDTO, WidgetUpdate

router = APIRouter(prefix="/widgets", tags=["widgets"])


def _owned_widget(db: Session, user: User, widget_id: UUID) -> Widget:
    widget = db.scalar(select(Widget).where(Widget.id == widget_id, Widget.user_id == user.id))
    if widget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found")
    return widget


@router.post("", response_model=WidgetDTO, status_code=status.HTTP_201_CREATED)
def create_widget(
    payload: WidgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Widget:
    widget = Widget(user_id=current_user.id, **payload.model_dump())
    db.add(widget)
    db.commit()
    db.refresh(widget)
    return widget


@router.get("", response_model=list[WidgetDTO])
def list_widgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Widget]:
    return list(db.scalars(select(Widget).where(Widget.user_id == current_user.id).order_by(Widget.created_at.desc())).all())


@router.get("/{widget_id}", response_model=WidgetDTO)
def get_widget(
    widget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Widget:
    return _owned_widget(db, current_user, widget_id)


@router.put("/{widget_id}", response_model=WidgetDTO)
def update_widget(
    widget_id: UUID,
    payload: WidgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Widget:
    widget = _owned_widget(db, current_user, widget_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(widget, field, value)
    db.commit()
    db.refresh(widget)
    return widget


@router.delete("/{widget_id}", response_model=WidgetDTO)
def delete_widget(
    widget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Widget:
    widget = _owned_widget(db, current_user, widget_id)
    widget.is_active = False
    db.commit()
    db.refresh(widget)
    return widget
