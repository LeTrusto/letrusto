import re
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.entities import AuditLog, Property, PropertyCampaign, SocialPost
from app.schemas.campaign import CHANNELS, STATUSES, CampaignCreate, CampaignUpdate, SocialPostInput


def _money(value: object) -> str:
    return f"INR {float(value):,.0f}" if value is not None else "Price on request"


def _property_facts(prop: Property) -> str:
    facts = [str(prop.bhk) + " BHK" if prop.bhk else None, f"{float(prop.built_up_area_sqft):,.0f} sq.ft" if prop.built_up_area_sqft else None]
    return " with ".join([item for item in facts if item])


def generate_posts(prop: Property, source: str, medium: str, content: str | None) -> list[SocialPostInput]:
    location = f"{prop.location.name}, {prop.location.city_name}"
    facts = _property_facts(prop)
    intro = f"{prop.title} in {location}\n\nA considered home with {facts}." if facts else f"{prop.title} in {location}\n\nA home presented with the details that matter."
    url = f"/properties/{prop.slug}?utm_source={source.lower()}&utm_medium={medium}&utm_campaign={{campaign_key}}&utm_content={content or 'property-post'}"
    cta = "View property"
    return [
        SocialPostInput(platform="INSTAGRAM", post_type="POST", headline=prop.title, body=f"{intro}\n\n{_money(prop.price_amount)}\n\nExplore the property:\n{url}\n\nInterested? Enquire directly.", cta=cta, content=content),
        SocialPostInput(platform="INSTAGRAM", post_type="REEL", headline=prop.title, body=f"Reel script\n\nOpen on {prop.title} in {location}.\nShow the spaces, details and light.\n{facts or 'A home presented with care'}.\n\n{_money(prop.price_amount)}\n\n{url}", cta=cta, content="property-reel"),
        SocialPostInput(platform="FACEBOOK", post_type="POST", headline=prop.title, body=f"{intro}\n\n{_money(prop.price_amount)} · {url}\n\nGet the property details and enquire directly.", cta=cta, content="property-post"),
        SocialPostInput(platform="WHATSAPP", post_type="SHARE_CARD", headline=prop.title, body=f"{prop.title}, {location}\n{facts or 'A thoughtfully presented home'}\n{_money(prop.price_amount)}\n\nView property: {url}\n\nInterested? Enquire directly.", cta=cta, content="property-share"),
    ]


class CampaignService:
    def __init__(self, db: Session):
        self.db = db

    def _validate(self, source: str, status: str) -> None:
        if source not in CHANNELS:
            raise BadRequestError("Unsupported campaign channel")
        if status not in STATUSES:
            raise BadRequestError("Invalid campaign status")

    def _property(self, property_id: UUID) -> Property:
        prop = self.db.scalar(select(Property).options(joinedload(Property.location), joinedload(Property.media)).where(Property.id == property_id))
        if not prop:
            raise NotFoundError("Property not found")
        if prop.status != "LIVE":
            raise BadRequestError("Campaigns can be created after the property is LIVE")
        return prop

    def _dto(self, campaign: PropertyCampaign):
        from app.schemas.campaign import CampaignDTO, SocialPostDTO
        return CampaignDTO(id=campaign.id, property_id=campaign.property_id, property_title=campaign.property.title, property_slug=campaign.property.slug, campaign_title=campaign.campaign_title, campaign_key=campaign.campaign_key, campaign_description=campaign.campaign_description, source=campaign.source, medium=campaign.medium, content=campaign.content, status=campaign.status, public_path=campaign.public_path or f"/properties/{campaign.property.slug}", social_posts=[SocialPostDTO.model_validate(post) for post in campaign.social_posts], created_at=campaign.created_at, updated_at=campaign.updated_at)

    def create(self, admin_id: UUID, property_id: UUID, payload: CampaignCreate):
        prop = self._property(property_id)
        self._validate(payload.source, payload.status)
        if self.db.scalar(select(PropertyCampaign).where(PropertyCampaign.property_id == property_id, PropertyCampaign.campaign_key == payload.campaign_key)):
            raise BadRequestError("Campaign key already exists for this property")
        posts = payload.social_posts or generate_posts(prop, payload.source, payload.medium, payload.content)
        if any(post.platform not in CHANNELS for post in posts):
            raise BadRequestError("Unsupported social channel")
        campaign = PropertyCampaign(property_id=property_id, campaign_title=payload.campaign_title, campaign_key=payload.campaign_key, campaign_description=payload.campaign_description, source=payload.source, medium=payload.medium, content=payload.content, status=payload.status, public_path=f"/properties/{prop.slug}")
        campaign.social_posts = [SocialPost(platform=post.platform, post_type=post.post_type, headline=post.headline, body=post.body.replace("{campaign_key}", payload.campaign_key), cta=post.cta, content=post.content) for post in posts]
        self.db.add(campaign)
        self.db.flush()
        self.db.add(AuditLog(actor_user_id=admin_id, entity_type="CAMPAIGN", entity_id=campaign.id, action="CAMPAIGN_CREATED", metadata_json={"property_id": str(property_id)}))
        self.db.commit()
        return self.get(campaign.id)

    def get(self, campaign_id: UUID):
        campaign = self.db.scalar(select(PropertyCampaign).options(joinedload(PropertyCampaign.property), joinedload(PropertyCampaign.social_posts)).where(PropertyCampaign.id == campaign_id))
        if not campaign:
            raise NotFoundError("Campaign not found")
        return self._dto(campaign)

    def list(self, property_id: UUID):
        return [self._dto(item) for item in self.db.scalars(select(PropertyCampaign).options(joinedload(PropertyCampaign.property), joinedload(PropertyCampaign.social_posts)).where(PropertyCampaign.property_id == property_id).order_by(PropertyCampaign.created_at.desc())).unique()]

    def update(self, admin_id: UUID, campaign_id: UUID, payload: CampaignUpdate):
        campaign = self.db.get(PropertyCampaign, campaign_id)
        if not campaign:
            raise NotFoundError("Campaign not found")
        values = payload.model_dump(exclude_unset=True)
        posts = values.pop("social_posts", None)
        if values.get("source") or values.get("status"):
            self._validate(values.get("source", campaign.source), values.get("status", campaign.status))
        for key, value in values.items():
            setattr(campaign, key, value)
        if posts is not None:
            posts = [SocialPostInput.model_validate(post) for post in posts]
            if any(post.platform not in CHANNELS for post in posts):
                raise BadRequestError("Unsupported social channel")
            campaign.social_posts = [SocialPost(platform=post.platform, post_type=post.post_type, headline=post.headline, body=post.body, cta=post.cta, content=post.content) for post in posts]
        self.db.add(AuditLog(actor_user_id=admin_id, entity_type="CAMPAIGN", entity_id=campaign.id, action="CAMPAIGN_EDITED"))
        self.db.commit()
        return self.get(campaign.id)