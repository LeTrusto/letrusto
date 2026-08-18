from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_order_service
from app.models.entities import User
from app.schemas.orders import CartDTO, CartItemRequest, CreateOrderRequest, OrderDTO
from app.services.order_service import OrderService

router = APIRouter(tags=["orders"])


@router.get("/cart", response_model=CartDTO)
def get_cart(current_user: User = Depends(get_current_user), service: OrderService = Depends(get_order_service)) -> CartDTO:
    return service.get_cart(current_user)


@router.post("/cart/items", response_model=CartDTO)
def add_cart_item(payload: CartItemRequest, current_user: User = Depends(get_current_user), service: OrderService = Depends(get_order_service)) -> CartDTO:
    return service.add_cart_item(current_user, payload)


@router.patch("/cart/items/{item_id}", response_model=CartDTO)
def update_cart_item(item_id: UUID, payload: CartItemRequest, current_user: User = Depends(get_current_user), service: OrderService = Depends(get_order_service)) -> CartDTO:
    return service.update_cart_item(current_user, item_id, payload.quantity)


@router.delete("/cart/items/{item_id}", response_model=CartDTO)
def remove_cart_item(item_id: UUID, current_user: User = Depends(get_current_user), service: OrderService = Depends(get_order_service)) -> CartDTO:
    return service.remove_cart_item(current_user, item_id)


@router.delete("/cart", response_model=CartDTO)
def clear_cart(current_user: User = Depends(get_current_user), service: OrderService = Depends(get_order_service)) -> CartDTO:
    return service.clear_cart(current_user)


@router.post("/orders", response_model=OrderDTO)
def create_order(payload: CreateOrderRequest, current_user: User = Depends(get_current_user), service: OrderService = Depends(get_order_service)) -> OrderDTO:
    return service.create_order(current_user, payload)


@router.get("/orders/{order_id}", response_model=OrderDTO)
def get_order(order_id: UUID, current_user: User = Depends(get_current_user), service: OrderService = Depends(get_order_service)) -> OrderDTO:
    return service.get_order(current_user, order_id)