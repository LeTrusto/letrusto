from uuid import UUID

from sqlalchemy.orm import Session

from app.models.entities import AuditLog


class AuditService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record(self, *, actor_user_id: UUID | None, entity_type: str, entity_id: UUID, action: str, metadata: dict | None = None) -> AuditLog:
        record = AuditLog(
            actor_user_id=actor_user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            metadata_json=metadata,
        )
        self.db.add(record)
        self.db.flush()
        return record
