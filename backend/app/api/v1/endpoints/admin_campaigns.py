from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.models.entities import PropertyCampaign, User
from app.schemas.campaign import CampaignCreate, CampaignDTO, CampaignUpdate
from app.services.campaign_service import CampaignService

router = APIRouter(prefix="/admin", tags=["admin-campaigns"])


@router.get("/properties/{property_id}/campaigns", response_model=list[CampaignDTO])
def list_campaigns(property_id: UUID, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return CampaignService(db).list(property_id)


@router.post("/properties/{property_id}/campaigns", response_model=CampaignDTO, status_code=201)
def create_campaign(property_id: UUID, payload: CampaignCreate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return CampaignService(db).create(admin.id, property_id, payload)


@router.get("/campaigns/{campaign_id}", response_model=CampaignDTO)
def get_campaign(campaign_id: UUID, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return CampaignService(db).get(campaign_id)


@router.patch("/campaigns/{campaign_id}", response_model=CampaignDTO)
def update_campaign(campaign_id: UUID, payload: CampaignUpdate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return CampaignService(db).update(admin.id, campaign_id, payload)
