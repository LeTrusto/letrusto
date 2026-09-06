from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import User, Widget, WidgetEvent, WidgetUsage
from app.services.entitlement_service import get_entitlement
from app.schemas.widgets import PublicWidgetDTO, PublicWidgetEventDTO

router = APIRouter(prefix="/public/embed", tags=["public-embed"])


@router.get("/{widget_id}", response_model=PublicWidgetDTO)
def get_public_widget(
    widget_id: UUID,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
) -> PublicWidgetDTO:
    response.headers["Cache-Control"] = "public, max-age=60"

    widget = db.scalar(select(Widget).where(Widget.id == widget_id, Widget.is_active.is_(True)))
    if widget is None:
        return JSONResponse(
            status_code=404,
            content={"detail": "Widget not found"},
        )  # type: ignore[return-value]

    origin = request.headers.get("origin")
    if not _origin_matches_domain(origin, widget.domain_name):
        return JSONResponse(status_code=403, content={"detail": "Widget domain is not allowed"})  # type: ignore[return-value]

    response.headers["Access-Control-Allow-Origin"] = origin or ""
    response.headers["Vary"] = "Origin"

    owner = db.scalar(select(User).where(User.id == widget.user_id))
    if owner is None:
        return JSONResponse(status_code=404, content={"detail": "Widget owner not found"})  # type: ignore[return-value]
    entitlement = get_entitlement(db, owner)
    period_start = date.today().replace(day=1)
    usage = db.scalar(
        select(WidgetUsage).where(WidgetUsage.widget_id == widget.id, WidgetUsage.period_start == period_start)
    )
    if usage is None:
        usage = WidgetUsage(widget_id=widget.id, period_start=period_start, view_count=0)
        db.add(usage)
    if entitlement.monthly_view_limit is not None and usage.view_count >= entitlement.monthly_view_limit:
        db.rollback()
        return JSONResponse(status_code=429, content={"detail": "Monthly widget view limit reached"})  # type: ignore[return-value]
    usage.view_count += 1
    db.commit()

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


def _origin_matches_domain(origin: str | None, configured_domain: str | None) -> bool:
    if not origin or not configured_domain:
        return False

    configured = configured_domain.strip().lower().rstrip("/")
    if not configured or configured in {"*", "null"}:
        return False
    if "://" in configured:
        configured = urlsplit(configured).netloc.lower()
    configured = configured.split("/", 1)[0]

    try:
        parsed = urlsplit(origin)
    except ValueError:
        return False
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False

    origin_host = parsed.hostname.lower()
    configured_host = configured.split(":", 1)[0].lstrip("www.")
    if origin_host != configured_host and not origin_host.endswith(f".{configured_host}"):
        return False

    configured_port = configured.rsplit(":", 1)[-1] if ":" in configured else None
    if configured_port and configured_port.isdigit():
        return str(parsed.port or (443 if parsed.scheme == "https" else 80)) == configured_port
    return True
