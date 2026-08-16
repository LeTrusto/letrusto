import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_admin
from app.models.entities import User
from app.schemas.supplier_discovery import SupplierDiscoveryResponse
from app.services.supplier_discovery_service import (
    SupplierAuthenticationError,
    SupplierDiscoveryService,
)
from app.suppliers.factory import build_supplier_adapter


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/supplier-discovery", tags=["admin", "supplier-discovery"])


@router.get("", response_model=SupplierDiscoveryResponse)
async def discover_supplier_products(
    keyword: str = Query(..., min_length=1, max_length=160),
    destination: str = Query("IN", pattern="^[A-Z]{2}$"),
    page_size: int = Query(20, ge=1, le=50),
    _: User = Depends(get_current_admin),
) -> SupplierDiscoveryResponse:
    try:
        adapter = build_supplier_adapter("cj")
        return await SupplierDiscoveryService(adapter).discover(
            keyword=keyword.strip(),
            destination=destination,
            page_size=page_size,
        )
    except SupplierAuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="CJ supplier authentication failed",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CJ supplier discovery is not configured",
        ) from exc
    except httpx.HTTPError as exc:
        logger.warning("CJ supplier discovery transport failed: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="CJ supplier discovery request failed",
        ) from exc