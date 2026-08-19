from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.entities import Product, TrustClaim, TrustClaimEvidence, TrustEvidence


class TrustRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _claim_options() -> tuple:
        return (
            selectinload(TrustClaim.evidence_links).selectinload(TrustClaimEvidence.evidence),
            selectinload(TrustClaim.verifications),
            selectinload(TrustClaim.audit_events),
        )

    def get_product(self, product_id: UUID) -> Product | None:
        return self.db.get(Product, product_id)

    def get_claim(self, claim_id: UUID) -> TrustClaim | None:
        statement = select(TrustClaim).where(TrustClaim.id == claim_id).options(*self._claim_options())
        return self.db.scalars(statement).unique().first()

    def list_product_claims(self, product_id: UUID) -> list[TrustClaim]:
        statement = (
            select(TrustClaim)
            .where(TrustClaim.product_id == product_id)
            .options(*self._claim_options())
            .order_by(TrustClaim.created_at.desc())
        )
        return list(self.db.scalars(statement).unique().all())

    def get_evidence(self, evidence_id: UUID) -> TrustEvidence | None:
        return self.db.get(TrustEvidence, evidence_id)
