from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class AdminInventoryReservationDTO(BaseModel):
    id: UUID
    order_number: str
    product_name: str
    variant_name: str
    variant_id: UUID
    quantity: int
    status: str
    created_at: str
    expires_at: str
    released_at: str | None = None
    consumed_at: str | None = None