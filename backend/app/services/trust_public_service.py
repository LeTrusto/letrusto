from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import NotFoundError
from app.core.trust import TRUST_VERIFICATION_METHOD_LABELS
from app.models.entities import Product, TrustClaim, TrustClaimEvidence
from app.schemas.trust_public import PublicTrustClaimDTO, PublicTrustEvidenceSummary, PublicTrustResponse


class PublicTrustService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_product_trust(self, product_slug: str) -> PublicTrustResponse:
        statement = (
            select(Product)
            .where(Product.slug == product_slug, Product.status == "ACTIVE")
            .options(
                selectinload(Product.trust_claims).selectinload(TrustClaim.verifications),
                selectinload(Product.trust_claims).selectinload(TrustClaim.evidence_links).selectinload(TrustClaimEvidence.evidence),
            )
        )
        product = self.db.scalars(statement).unique().first()
        if product is None:
            raise NotFoundError(f"Product '{product_slug}' not found")

        claims: list[PublicTrustClaimDTO] = []
        for claim in sorted(product.trust_claims, key=lambda item: item.created_at, reverse=True):
            if claim.verification_status == "REJECTED":
                continue

            verification = max(claim.verifications, key=lambda item: item.verified_at, default=None)
            status = claim.verification_status
            if status == "VERIFIED" and verification and verification.expires_at and verification.expires_at <= datetime.now(timezone.utc):
                status = "EXPIRED"

            evidence_by_id = {
                str(link.evidence_id): link.evidence
                for link in claim.evidence_links
                if link.evidence is not None
            }
            evidence_summary = []
            if status in {"VERIFIED", "EXPIRED"} and verification and verification.evidence_snapshot:
                evidence_summary = [
                    PublicTrustEvidenceSummary(
                        evidence_type=str(item.get("evidence_type", "Supporting evidence")),
                        title=str(item.get("title", "Evidence reviewed")),
                        description=evidence_by_id.get(str(item.get("evidence_id"))).description if evidence_by_id.get(str(item.get("evidence_id"))) else None,
                    )
                    for item in verification.evidence_snapshot
                ]

            claims.append(PublicTrustClaimDTO(
                claim_type=claim.claim_type,
                claim_value=claim.claim_value,
                status=status,
                verified_at=verification.verified_at if verification else None,
                verification_method=TRUST_VERIFICATION_METHOD_LABELS.get(verification.verification_method) if verification else None,
                evidence_summary=evidence_summary,
            ))

        return PublicTrustResponse(product_id=product.slug, claims=claims)