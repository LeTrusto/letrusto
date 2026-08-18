from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReconciliationIssueDTO(BaseModel):
    order_id: UUID
    order_number: str
    code: str
    detail: str


class ReconciliationResultDTO(BaseModel):
    started_at: datetime
    completed_at: datetime
    reservations_expired: int = 0
    payments_reconciled: int = 0
    fulfillment_submitted: int = 0
    tracking_synced: int = 0
    inconsistencies_found: int = 0
    failures: list[str] = []
    provider_unavailable: list[str] = []
    inconsistencies: list[ReconciliationIssueDTO] = []
