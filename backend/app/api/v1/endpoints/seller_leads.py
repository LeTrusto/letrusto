from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.entities import User
from app.schemas.enquiry import LeadStatusUpdate, SellerEnquiryDTO
from app.services.enquiry_service import EnquiryService

router = APIRouter(prefix="/seller", tags=["seller-leads"])


@router.get("/properties/{property_id}/enquiries", response_model=list[SellerEnquiryDTO])
def list_enquiries(property_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = EnquiryService(db)
    return [service.to_seller_dto(row) for row in service.list_for_seller(current_user, property_id)]


@router.get("/enquiries", response_model=list[SellerEnquiryDTO])
def list_all_enquiries(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = EnquiryService(db)
    return [service.to_seller_dto(row) for row in service.list_all_for_seller(current_user)]


@router.get("/enquiries/{enquiry_id}", response_model=SellerEnquiryDTO)
def get_enquiry(enquiry_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = EnquiryService(db)
    return service.to_seller_dto(service.get_for_seller(current_user, enquiry_id))


@router.patch("/enquiries/{enquiry_id}", response_model=SellerEnquiryDTO)
def update_enquiry(enquiry_id: UUID, payload: LeadStatusUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = EnquiryService(db)
    updated = service.update_status(current_user, enquiry_id, payload)
    return service.to_seller_dto(updated if current_user.role == "admin" else service.get_for_seller(current_user, updated.id))
