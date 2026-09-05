from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import User, Widget, WidgetEvent
from app.schemas.widgets import WidgetEventCreate, WidgetEventDTO

router = APIRouter(tags=["widget-events"])


def _owned_widget(db: Session, user: User, widget_id: UUID) -> Widget:
    widget = db.scalar(select(Widget).where(Widget.id == widget_id, Widget.user_id == user.id))
    if widget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found")
    return widget


def _owned_event(db: Session, user: User, event_id: UUID) -> WidgetEvent:
    event = db.scalar(
        select(WidgetEvent)
        .join(Widget, Widget.id == WidgetEvent.widget_id)
        .where(WidgetEvent.id == event_id, Widget.user_id == user.id)
    )
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget event not found")
    return event


@router.post("/widgets/{widget_id}/events", response_model=WidgetEventDTO, status_code=status.HTTP_201_CREATED)
def create_widget_event(
    widget_id: UUID,
    payload: WidgetEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WidgetEvent:
    _owned_widget(db, current_user, widget_id)
    event = WidgetEvent(widget_id=widget_id, **payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/widgets/{widget_id}/events", response_model=list[WidgetEventDTO])
def list_widget_events(
    widget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[WidgetEvent]:
    _owned_widget(db, current_user, widget_id)
    return list(
        db.scalars(
            select(WidgetEvent)
            .where(WidgetEvent.widget_id == widget_id)
            .order_by(WidgetEvent.created_at.desc())
        ).all()
    )


@router.delete("/events/{event_id}", response_model=WidgetEventDTO)
def hide_widget_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WidgetEvent:
    event = _owned_event(db, current_user, event_id)
    event.is_approved = False
    db.commit()
    db.refresh(event)
    return event
