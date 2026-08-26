from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request

from app.api.deps import get_cancellation_service, get_cashfree_service, get_current_admin, get_current_user, get_order_service, get_razorpay_service, get_stripe_service
from app.models.entities import User
from app.schemas.cancellation import AdminCancelRequest, CancelOrderRequest, CancellationStatusDTO, RefundDTO
from app.schemas.orders import CartDTO, CartItemRequest, CreateOrderRequest, OrderDTO
from app.services.order_service import OrderService
from app.schemas.payments import PaymentSessionDTO, PaymentStatusDTO, RazorpayOrderDTO, RazorpayPaymentVerification, StripeCheckoutSessionDTO
from app.services.cancellation_service import CancellationService
from app.services.cashfree_service import CashfreeService
from app.services.razorpay_service import RazorpayService
from app.services.stripe_service import StripeService

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


@router.post("/orders/{order_id}/razorpay-order", response_model=RazorpayOrderDTO)
def create_razorpay_order(order_id: UUID, current_user: User = Depends(get_current_user), service: RazorpayService = Depends(get_razorpay_service)) -> RazorpayOrderDTO:
    return service.create_order(current_user, order_id)


@router.post("/orders/{order_id}/razorpay/verify", response_model=PaymentStatusDTO)
async def verify_razorpay_payment(order_id: UUID, payload: RazorpayPaymentVerification, current_user: User = Depends(get_current_user), service: RazorpayService = Depends(get_razorpay_service)) -> PaymentStatusDTO:
    return await service.verify_payment(current_user, order_id, payload)


@router.get("/orders/{order_id}/razorpay/payment-status", response_model=PaymentStatusDTO)
async def verify_razorpay_payment_status(order_id: UUID, current_user: User = Depends(get_current_user), service: RazorpayService = Depends(get_razorpay_service)) -> PaymentStatusDTO:
    return await service.verify_payment_status(current_user, order_id)


@router.post("/payments/razorpay/webhook", status_code=200)
async def razorpay_webhook(request: Request, x_razorpay_signature: str | None = Header(default=None), service: RazorpayService = Depends(get_razorpay_service)) -> dict[str, str]:
    await service.process_webhook(await request.body(), x_razorpay_signature)
    return {"status": "ok"}


@router.post("/orders/{order_id}/stripe-session", response_model=StripeCheckoutSessionDTO)
def create_stripe_session(order_id: UUID, current_user: User = Depends(get_current_user), service: StripeService = Depends(get_stripe_service)) -> StripeCheckoutSessionDTO:
    return service.create_session(current_user, order_id)


@router.post("/payments/stripe/webhook", status_code=200)
async def stripe_webhook(request: Request, stripe_signature: str | None = Header(default=None, alias="stripe-signature"), service: StripeService = Depends(get_stripe_service)) -> dict[str, str]:
    await service.process_webhook(await request.body(), stripe_signature)
    return {"status": "ok"}


@router.post("/orders/{order_id}/cashfree-session", response_model=PaymentSessionDTO)
def create_cashfree_session(order_id: UUID, current_user: User = Depends(get_current_user), service: CashfreeService = Depends(get_cashfree_service)) -> PaymentSessionDTO:
    return service.create_session(current_user, order_id)


@router.get("/orders/{order_id}/payment-status", response_model=PaymentStatusDTO)
async def verify_cashfree_payment(order_id: UUID, current_user: User = Depends(get_current_user), service: CashfreeService = Depends(get_cashfree_service)) -> PaymentStatusDTO:
    return await service.verify_payment(current_user, order_id)


@router.post("/payments/cashfree/webhook", status_code=200)
async def cashfree_webhook(request: Request, x_webhook_timestamp: str | None = Header(default=None), x_webhook_signature: str | None = Header(default=None), service: CashfreeService = Depends(get_cashfree_service)) -> dict[str, str]:
    await request.body()
    await service.process_webhook(await request.body(), x_webhook_timestamp, x_webhook_signature)
    return {"status": "ok"}


# ── Cancellation ──────────────────────────────────────────


@router.post("/orders/{order_id}/cancel", response_model=CancellationStatusDTO)
def cancel_order(order_id: UUID, payload: CancelOrderRequest | None = None, current_user: User = Depends(get_current_user), service: CancellationService = Depends(get_cancellation_service)) -> CancellationStatusDTO:
    reason = payload.reason if payload else "Customer requested cancellation"
    order = service.cancel_by_customer(current_user, order_id, reason)
    refund = service.get_refund_status(order.id)
    return _build_cancellation_dto(order, refund)


@router.post("/admin/orders/{order_id}/cancel", response_model=CancellationStatusDTO)
def admin_cancel_order(order_id: UUID, payload: AdminCancelRequest | None = None, admin: User = Depends(get_current_admin), service: CancellationService = Depends(get_cancellation_service)) -> CancellationStatusDTO:
    reason = payload.reason if payload else "Admin cancellation"
    order = service.cancel_by_admin(admin, order_id, reason)
    refund = service.get_refund_status(order.id)
    return _build_cancellation_dto(order, refund)


@router.get("/admin/orders/{order_id}/refund", response_model=RefundDTO | None)
def admin_get_refund(order_id: UUID, _: User = Depends(get_current_admin), service: CancellationService = Depends(get_cancellation_service)) -> RefundDTO | None:
    refund = service.get_refund_status(order_id)
    if refund is None:
        return None
    return RefundDTO(id=refund.id, order_id=refund.order_id, provider=refund.provider, provider_refund_id=refund.provider_refund_id, amount=refund.amount, currency=refund.currency, status=refund.status, reason=refund.reason, requested_by=refund.requested_by, requested_at=refund.requested_at.isoformat(), completed_at=refund.completed_at.isoformat() if refund.completed_at else None, failed_at=refund.failed_at.isoformat() if refund.failed_at else None, failure_reason=refund.failure_reason)


@router.post("/admin/orders/{order_id}/refund/retry", response_model=RefundDTO)
def admin_retry_refund(order_id: UUID, admin: User = Depends(get_current_admin), service: CancellationService = Depends(get_cancellation_service)) -> RefundDTO:
    refund = service.retry_failed_refund(admin, order_id)
    return RefundDTO(id=refund.id, order_id=refund.order_id, provider=refund.provider, provider_refund_id=refund.provider_refund_id, amount=refund.amount, currency=refund.currency, status=refund.status, reason=refund.reason, requested_by=refund.requested_by, requested_at=refund.requested_at.isoformat(), completed_at=refund.completed_at.isoformat() if refund.completed_at else None, failed_at=refund.failed_at.isoformat() if refund.failed_at else None, failure_reason=refund.failure_reason)


def _build_cancellation_dto(order, refund) -> CancellationStatusDTO:
    refund_msg = None
    if refund:
        if refund.status == "SUCCESS":
            refund_msg = "Refund has been processed successfully."
        elif refund.status == "PROCESSING":
            refund_msg = "Refund is being processed. Please allow 5-7 business days."
        elif refund.status == "PENDING":
            refund_msg = "Refund has been initiated and is awaiting processing."
        elif refund.status == "FAILED":
            refund_msg = "Refund could not be processed. Please contact support."

    return CancellationStatusDTO(
        order_id=order.id,
        order_status=order.status,
        payment_status=order.payment_status,
        fulfillment_status=order.fulfillment_status,
        cancellation_reason=order.cancellation_reason,
        cancelled_at=order.cancelled_at.isoformat() if order.cancelled_at else None,
        refund_status=refund.status if refund else None,
        refund_amount=refund.amount if refund else None,
        refund_message=refund_msg,
    )