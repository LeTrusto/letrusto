from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

import razorpay
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.entities import PropertyContactUnlock, PropertyListing, PropertyPaymentAttempt, User
from app.schemas.properties import (
    PropertyListingCreateRequest,
    PropertyListingDTO,
    PropertyListingPage,
    PropertyModerationRequest,
    PropertyPaymentOrderDTO,
    PropertyPaymentVerification,
)

# Placeholder pricing — adjust to your actual business decision before real launch.
LISTING_FEE = Decimal("199.00")
CONTACT_UNLOCK_FEE = Decimal("49.00")
CURRENCY = "INR"
PROVIDER = "RAZORPAY"


class PropertyService:
    def __init__(self, db: Session, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings or get_settings()

    def _client(self) -> razorpay.Client:
        if not self.settings.RAZORPAY_KEY_ID or not self.settings.RAZORPAY_KEY_SECRET:
            raise HTTPException(status_code=503, detail="Payments are not configured")
        return razorpay.Client(auth=(self.settings.RAZORPAY_KEY_ID, self.settings.RAZORPAY_KEY_SECRET))

    def _dto(self, listing: PropertyListing, user: User | None) -> PropertyListingDTO:
        is_owner = bool(user and listing.seller_user_id == user.id)
        is_admin = bool(user and user.role == "admin")
        unlocked = is_owner or is_admin
        if not unlocked and user:
            unlocked = self.db.scalar(
                select(PropertyContactUnlock).where(
                    PropertyContactUnlock.listing_id == listing.id,
                    PropertyContactUnlock.buyer_user_id == user.id,
                )
            ) is not None
        return PropertyListingDTO(
            id=listing.id, property_type=listing.property_type, title=listing.title, description=listing.description,
            locality=listing.locality, city=listing.city, price=listing.price, area_sqft=listing.area_sqft,
            bedrooms=listing.bedrooms, image_urls=listing.image_urls or [], status=listing.status,
            is_featured=listing.is_featured, is_own_listing=is_owner, contact_unlocked=unlocked,
            contact_name=listing.contact_name if unlocked else None,
            contact_phone=listing.contact_phone if unlocked else None,
            contact_email=listing.contact_email if unlocked else None,
            created_at=listing.created_at.isoformat(),
        )

    def create_listing(self, user: User, payload: PropertyListingCreateRequest) -> PropertyPaymentOrderDTO:
        listing = PropertyListing(
            seller_user_id=user.id, property_type=payload.property_type, title=payload.title,
            description=payload.description, locality=payload.locality, price=payload.price,
            area_sqft=payload.area_sqft, bedrooms=payload.bedrooms, image_urls=payload.image_urls,
            contact_name=payload.contact_name, contact_phone=payload.contact_phone, contact_email=payload.contact_email,
            status="PENDING_PAYMENT",
        )
        self.db.add(listing)
        self.db.flush()
        order = self._create_payment_order(user, listing, purpose="LISTING_FEE", amount=LISTING_FEE)
        self.db.commit()
        return order

    def _create_payment_order(self, user: User, listing: PropertyListing, purpose: str, amount: Decimal) -> PropertyPaymentOrderDTO:
        existing = self.db.scalar(
            select(PropertyPaymentAttempt).where(
                PropertyPaymentAttempt.user_id == user.id,
                PropertyPaymentAttempt.listing_id == listing.id,
                PropertyPaymentAttempt.purpose == purpose,
                PropertyPaymentAttempt.status == "PENDING",
            ).order_by(PropertyPaymentAttempt.created_at.desc())
        )
        if existing:
            provider_order_id = existing.provider_order_id
            attempt = existing
        else:
            amount_paise = int(amount * 100)
            try:
                provider_order = self._client().order.create({
                    "amount": amount_paise,
                    "currency": CURRENCY,
                    "receipt": f"prop-{purpose.lower()}-{listing.id}"[:40],
                    "notes": {"letrusto_listing_id": str(listing.id), "letrusto_user_id": str(user.id), "purpose": purpose},
                })
            except Exception as exc:
                raise HTTPException(status_code=502, detail="Payment order could not be created") from exc
            provider_order_id = str(provider_order.get("id") or "")
            if not provider_order_id:
                raise HTTPException(status_code=502, detail="Payment provider returned no order ID")
            attempt = PropertyPaymentAttempt(
                user_id=user.id, listing_id=listing.id, purpose=purpose, provider=PROVIDER,
                provider_order_id=provider_order_id, amount=amount, currency=CURRENCY,
            )
            self.db.add(attempt)
            self.db.flush()
        return PropertyPaymentOrderDTO(
            attempt_id=attempt.id, listing_id=listing.id, purpose=purpose, provider=PROVIDER,
            key_id=self.settings.RAZORPAY_KEY_ID, razorpay_order_id=provider_order_id,
            amount=int(amount * 100), currency=CURRENCY,
        )

    def _verify_payment(self, user: User, listing: PropertyListing, purpose: str, amount: Decimal, payload: PropertyPaymentVerification) -> PropertyPaymentAttempt:
        attempt = self.db.scalar(
            select(PropertyPaymentAttempt).where(
                PropertyPaymentAttempt.user_id == user.id,
                PropertyPaymentAttempt.listing_id == listing.id,
                PropertyPaymentAttempt.purpose == purpose,
                PropertyPaymentAttempt.provider_order_id == payload.razorpay_order_id,
            ).with_for_update()
        )
        if attempt is None:
            raise HTTPException(status_code=404, detail="Payment attempt not found")
        if attempt.status == "VERIFIED":
            if attempt.provider_payment_id != payload.razorpay_payment_id:
                raise HTTPException(status_code=409, detail="Payment attempt already has a different payment")
            return attempt
        if attempt.provider_payment_id and attempt.provider_payment_id != payload.razorpay_payment_id:
            raise HTTPException(status_code=409, detail="Payment attempt already has a different payment")
        try:
            client = self._client()
            provider_order = client.order.fetch(payload.razorpay_order_id)
            payment = client.payment.fetch(payload.razorpay_payment_id)
            client.utility.verify_payment_signature({
                "razorpay_order_id": payload.razorpay_order_id,
                "razorpay_payment_id": payload.razorpay_payment_id,
                "razorpay_signature": payload.razorpay_signature,
            })
        except Exception as exc:
            raise HTTPException(status_code=422, detail="Invalid payment signature or payment details") from exc
        expected = int(amount * 100)
        if (
            str(provider_order.get("id") or "") != payload.razorpay_order_id
            or int(provider_order.get("amount") or 0) != expected
            or str(provider_order.get("currency") or "") != CURRENCY
            or str(payment.get("order_id") or "") != payload.razorpay_order_id
            or int(payment.get("amount") or 0) != expected
            or str(payment.get("currency") or "") != CURRENCY
            or str(payment.get("status") or "").lower() != "captured"
        ):
            raise HTTPException(status_code=422, detail="Payment does not match the expected order")
        attempt.provider_payment_id = payload.razorpay_payment_id
        attempt.status = "VERIFIED"
        self.db.flush()
        return attempt

    def verify_listing_payment(self, user: User, listing_id: UUID, payload: PropertyPaymentVerification) -> PropertyListingDTO:
        listing = self._owned_listing(user, listing_id)
        self._verify_payment(user, listing, "LISTING_FEE", LISTING_FEE, payload)
        if listing.status == "PENDING_PAYMENT":
            listing.status = "PENDING_REVIEW"
        self.db.commit()
        self.db.refresh(listing)
        return self._dto(listing, user)

    def request_contact_unlock(self, user: User, listing_id: UUID) -> PropertyPaymentOrderDTO:
        listing = self._visible_listing(listing_id, user)
        if listing.seller_user_id == user.id:
            raise HTTPException(status_code=400, detail="You cannot purchase your own listing's contact details")
        already = self.db.scalar(
            select(PropertyContactUnlock).where(
                PropertyContactUnlock.listing_id == listing.id, PropertyContactUnlock.buyer_user_id == user.id
            )
        )
        if already:
            raise HTTPException(status_code=409, detail="Contact details are already unlocked for this listing")
        order = self._create_payment_order(user, listing, purpose="CONTACT_UNLOCK", amount=CONTACT_UNLOCK_FEE)
        self.db.commit()
        return order

    def verify_contact_unlock(self, user: User, listing_id: UUID, payload: PropertyPaymentVerification) -> PropertyListingDTO:
        listing = self._visible_listing(listing_id, user)
        attempt = self._verify_payment(user, listing, "CONTACT_UNLOCK", CONTACT_UNLOCK_FEE, payload)
        unlock = self.db.scalar(select(PropertyContactUnlock).where(PropertyContactUnlock.payment_attempt_id == attempt.id))
        if unlock is None:
            unlock = PropertyContactUnlock(listing_id=listing.id, buyer_user_id=user.id, payment_attempt_id=attempt.id)
            self.db.add(unlock)
        self.db.commit()
        self.db.refresh(listing)
        return self._dto(listing, user)

    def _owned_listing(self, user: User, listing_id: UUID) -> PropertyListing:
        listing = self.db.get(PropertyListing, listing_id)
        if listing is None or listing.seller_user_id != user.id:
            raise HTTPException(status_code=404, detail="Listing not found")
        return listing

    def _visible_listing(self, listing_id: UUID, user: User | None) -> PropertyListing:
        listing = self.db.get(PropertyListing, listing_id)
        if listing is None:
            raise HTTPException(status_code=404, detail="Listing not found")
        is_owner = bool(user and listing.seller_user_id == user.id)
        is_admin = bool(user and user.role == "admin")
        if listing.status != "APPROVED" and not is_owner and not is_admin:
            raise HTTPException(status_code=404, detail="Listing not found")
        return listing

    def get_listing(self, listing_id: UUID, user: User | None) -> PropertyListingDTO:
        return self._dto(self._visible_listing(listing_id, user), user)

    def list_listings(
        self, user: User | None, property_type: str | None, locality: str | None,
        min_price: Decimal | None, max_price: Decimal | None, page: int, page_size: int,
    ) -> PropertyListingPage:
        query = select(PropertyListing).where(PropertyListing.status == "APPROVED")
        if property_type:
            query = query.where(PropertyListing.property_type == property_type)
        if locality:
            query = query.where(PropertyListing.locality.ilike(f"%{locality}%"))
        if min_price is not None:
            query = query.where(PropertyListing.price >= min_price)
        if max_price is not None:
            query = query.where(PropertyListing.price <= max_price)
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        rows = self.db.scalars(
            query.order_by(PropertyListing.is_featured.desc(), PropertyListing.created_at.desc())
            .offset((page - 1) * page_size).limit(page_size)
        ).all()
        return PropertyListingPage(items=[self._dto(row, user) for row in rows], total=total, page=page, page_size=page_size)

    def list_mine(self, user: User) -> list[PropertyListingDTO]:
        rows = self.db.scalars(
            select(PropertyListing).where(PropertyListing.seller_user_id == user.id).order_by(PropertyListing.created_at.desc())
        ).all()
        return [self._dto(row, user) for row in rows]

    def admin_list_pending(self) -> list[PropertyListingDTO]:
        rows = self.db.scalars(
            select(PropertyListing).where(PropertyListing.status == "PENDING_REVIEW").order_by(PropertyListing.created_at.asc())
        ).all()
        return [self._dto(row, None) for row in rows]

    def admin_moderate(self, listing_id: UUID, payload: PropertyModerationRequest) -> PropertyListingDTO:
        listing = self.db.get(PropertyListing, listing_id)
        if listing is None:
            raise HTTPException(status_code=404, detail="Listing not found")
        listing.status = "APPROVED" if payload.approve else "REJECTED"
        listing.moderation_reason = payload.reason
        listing.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(listing)
        return self._dto(listing, None)
