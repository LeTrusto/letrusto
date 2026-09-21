from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.entities import Location, Property, PropertyEnquiry, SellerProfile


class PropertyRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def seller_profile(self, user_id: UUID) -> SellerProfile | None:
        return self.db.scalar(select(SellerProfile).where(SellerProfile.user_id == user_id))

    def property_for_seller(self, property_id: UUID, user_id: UUID) -> Property | None:
        return self.db.scalar(
            select(Property).join(SellerProfile).where(Property.id == property_id, SellerProfile.user_id == user_id)
        )

    def by_slug_live(self, slug: str) -> Property | None:
        return self.db.scalar(
            select(Property).options(joinedload(Property.location), joinedload(Property.media)).where(
                Property.slug == slug, Property.status == "LIVE"
            )
        )

    def public(self, offset: int, limit: int) -> list[Property]:
        return list(self.db.scalars(
            select(Property).options(joinedload(Property.location), joinedload(Property.media)).where(
                Property.status == "LIVE"
            ).order_by(Property.published_at.desc()).offset(offset).limit(limit)
        ).unique())

    def enquiries_for_seller_property(self, enquiry_property_id: UUID, user_id: UUID) -> list[PropertyEnquiry]:
        return list(self.db.scalars(
            select(PropertyEnquiry).join(Property).join(SellerProfile).where(
                PropertyEnquiry.property_id == enquiry_property_id, SellerProfile.user_id == user_id
            ).order_by(PropertyEnquiry.created_at.desc())
        ))

    def locations(self) -> list[Location]:
        return list(self.db.scalars(select(Location).where(Location.is_active.is_(True)).order_by(Location.name)))
