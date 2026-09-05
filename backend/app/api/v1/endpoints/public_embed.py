from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Widget, WidgetEvent
from app.schemas.widgets import PublicWidgetDTO, PublicWidgetEventDTO

router = APIRouter(prefix="/public/embed", tags=["public-embed"])


@router.get("/{widget_id}", response_model=PublicWidgetDTO)
def get_public_widget(
    widget_id: UUID,
    response: Response,
    db: Session = Depends(get_db),
) -> PublicWidgetDTO:
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Cache-Control"] = "public, max-age=60"

    widget = db.scalar(select(Widget).where(Widget.id == widget_id, Widget.is_active.is_(True)))
    if widget is None:
        return JSONResponse(
            status_code=404,
            content={"detail": "Widget not found"},
            headers={"Access-Control-Allow-Origin": "*"},
        )  # type: ignore[return-value]

    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    events = db.scalars(
        select(WidgetEvent)
        .where(
            WidgetEvent.widget_id == widget.id,
            WidgetEvent.is_approved.is_(True),
            WidgetEvent.created_at >= cutoff,
        )
        .order_by(WidgetEvent.created_at.desc())
    ).all()
    return PublicWidgetDTO(
        id=widget.id,
        position=widget.position,
        theme_color=widget.theme_color,
        display_delay=widget.display_delay,
        events=[PublicWidgetEventDTO.model_validate(event) for event in events],
    )
