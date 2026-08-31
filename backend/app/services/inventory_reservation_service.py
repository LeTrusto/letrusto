from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.exceptions import BadRequestError
from app.models.entities import InventoryReservation, Order, OrderItem, ProductVariant

ACTIVE = "ACTIVE"
RELEASED = "RELEASED"
CONSUMED = "CONSUMED"
EXPIRED = "EXPIRED"


class InventoryReservationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def release_expired(self, now: datetime | None = None, *, commit: bool = True) -> int:
        now = now or datetime.now(timezone.utc)
        rows = list(self.db.scalars(
            select(InventoryReservation)
            .where(InventoryReservation.status == ACTIVE, InventoryReservation.expires_at <= now)
            .with_for_update()
        ).all())
        for reservation in rows:
            if reservation.status == ACTIVE and reservation.expires_at <= now:
                reservation.status = EXPIRED
                reservation.released_at = now
        expired = len(rows)
        if expired and commit:
            self.db.commit()
        return expired

    def active_quantity(self, variant_id: UUID, now: datetime | None = None) -> int:
        now = now or datetime.now(timezone.utc)
        self.release_expired(now, commit=False)
        return int(self.db.scalar(
            select(func.coalesce(func.sum(InventoryReservation.quantity), 0)).where(
                InventoryReservation.variant_id == variant_id,
                InventoryReservation.status == ACTIVE,
                InventoryReservation.expires_at > now,
            )
        ) or 0)

    def reserve_order(self, order: Order, variants_by_id: dict[UUID, ProductVariant], now: datetime | None = None) -> list[InventoryReservation]:
        now = now or datetime.now(timezone.utc)
        self.release_expired(now, commit=False)
        ttl = timedelta(minutes=get_settings().INVENTORY_RESERVATION_TTL_MINUTES)
        reservations: list[InventoryReservation] = []
        for item in order.items:
            variant = variants_by_id[item.variant_id]
            if item.product and item.product.supplier == "printful":
                continue
            cj_inventory = max(0, variant.cj_inventory or 0)
            reserved = self.active_quantity(variant.id, now)
            available = max(0, cj_inventory - reserved)
            if item.quantity > available:
                raise BadRequestError(f"Only {available} units are currently available for {item.product_name}")
            reservation = InventoryReservation(
                order=order,
                order_item=item,
                variant=variant,
                quantity=item.quantity,
                status=ACTIVE,
                expires_at=now + ttl,
            )
            self.db.add(reservation)
            reservations.append(reservation)
        self.db.flush()
        return reservations

    def consume_for_order(self, order_id: UUID, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        rows = list(self.db.scalars(
            select(InventoryReservation).where(InventoryReservation.order_id == order_id).with_for_update()
        ).all())
        if not rows:
            return True
        all_consumed = True
        for reservation in rows:
            if reservation.status == ACTIVE and reservation.expires_at > now:
                reservation.status = CONSUMED
                reservation.consumed_at = now
            elif reservation.status != CONSUMED:
                all_consumed = False
        return all_consumed

    def fulfillment_safe(self, order_id: UUID) -> bool:
        rows = list(self.db.scalars(select(InventoryReservation).where(InventoryReservation.order_id == order_id)).all())
        return not rows or all(row.status == CONSUMED for row in rows)

    def release_for_order(self, order_id: UUID, *, allow_submitted: bool = False, now: datetime | None = None) -> int:
        now = now or datetime.now(timezone.utc)
        order = self.db.get(Order, order_id)
        if order is not None and order.supplier_order_id and not allow_submitted:
            return 0
        rows = list(self.db.scalars(
            select(InventoryReservation).where(
                InventoryReservation.order_id == order_id,
                InventoryReservation.status == ACTIVE,
            ).with_for_update()
        ).all())
        for reservation in rows:
            reservation.status = RELEASED
            reservation.released_at = now
        return len(rows)

    def list_for_admin(self, order_id: UUID | None = None) -> list[InventoryReservation]:
        query = select(InventoryReservation).options(
            selectinload(InventoryReservation.order),
            selectinload(InventoryReservation.order_item),
            selectinload(InventoryReservation.variant),
        ).order_by(InventoryReservation.created_at.desc())
        if order_id is not None:
            query = query.where(InventoryReservation.order_id == order_id)
        return list(self.db.scalars(query).all())
