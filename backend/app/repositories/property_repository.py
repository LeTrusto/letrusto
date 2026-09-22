from uuid import UUID

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.entities import Location, Property, PropertyEnquiry, PropertyType, SellerProfile


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

    def public_page(
        self,
        *,
        page: int,
        page_size: int,
        property_type: PropertyType | None = None,
        bhk: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        locality: str | None = None,
        search: str | None = None,
        sort: str = "newest",
    ) -> tuple[list[Property], int]:
        filters = [Property.status == "LIVE"]
        if property_type:
            filters.append(Property.property_type == property_type.value)
        if bhk:
            filters.append(Property.bhk >= 4 if bhk == 4 else Property.bhk == bhk)
        if min_price is not None:
            filters.append(Property.price_amount >= min_price)
        if max_price is not None:
            filters.append(Property.price_amount <= max_price)
        if locality:
            term = f"%{locality.strip()}%"
            filters.append(or_(Location.slug.ilike(term), Location.name.ilike(term), Location.normalized_name.ilike(term)))
        if search:
            term = f"%{search.strip()}%"
            filters.append(or_(Property.title.ilike(term), Property.description.ilike(term), Location.name.ilike(term)))

        base = select(Property).join(Location).where(*filters)
        total = int(self.db.scalar(select(func.count()).select_from(base.subquery())) or 0)
        ordering = {
            "newest": (desc(Property.published_at), desc(Property.created_at)),
            "price_asc": (asc(Property.price_amount), desc(Property.created_at)),
            "price_desc": (desc(Property.price_amount), desc(Property.created_at)),
        }[sort]
        items = list(self.db.scalars(
            base.options(joinedload(Property.location), joinedload(Property.media))
            .order_by(*ordering)
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).unique())
        return items, total

    def enquiries_for_seller_property(self, enquiry_property_id: UUID, user_id: UUID) -> list[PropertyEnquiry]:
        return list(self.db.scalars(
            select(PropertyEnquiry).join(Property).join(SellerProfile).where(
                PropertyEnquiry.property_id == enquiry_property_id, SellerProfile.user_id == user_id
            ).order_by(PropertyEnquiry.created_at.desc())
        ))

    def locations(self) -> list[Location]:
        return list(self.db.scalars(select(Location).where(Location.is_active.is_(True)).order_by(Location.name)))
