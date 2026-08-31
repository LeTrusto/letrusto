import asyncio
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.core.config import get_settings
from app.models.entities import Cart, CartItem, Order, OrderItem, Product, ProductVariant, User
from app.schemas.orders import CartDTO, CartItemDTO, CartItemRequest, CreateOrderRequest, OrderDTO, OrderItemDTO, OrderListDTO, OrderQuoteDTO, OrderQuoteRequest
from app.services.inventory_reservation_service import InventoryReservationService
from app.services.fulfillment_preflight_service import FulfillmentPreflightService
from app.services.printful_shipping_service import PrintfulShippingService

# Razorpay is the only active provider and settles INR, so purchasing stays India-only.
INDIA_COUNTRY_CODES = frozenset({"IN", "INDIA"})
INTERNATIONAL_CHECKOUT_UNAVAILABLE = "INTERNATIONAL_CHECKOUT_UNAVAILABLE"


class OrderService:
    def __init__(self, db: Session, fulfillment_preflight_service: FulfillmentPreflightService | None = None) -> None:
        self.db = db
        self.fulfillment_preflight_service = fulfillment_preflight_service or FulfillmentPreflightService(db)

    def _cart(self, user: User) -> Cart:
        cart = self.db.scalar(
            select(Cart).where(Cart.user_id == user.id).options(selectinload(Cart.items).selectinload(CartItem.product), selectinload(Cart.items).selectinload(CartItem.variant))
        )
        if cart is None:
            cart = Cart(user_id=user.id)
            self.db.add(cart)
            self.db.flush()
        return cart

    @staticmethod
    def _resolve_variant(db: Session, product_id: str, variant_id: str) -> tuple[Product, ProductVariant]:
        product = db.scalar(
            select(Product).where(Product.slug == product_id, Product.status == "ACTIVE").options(selectinload(Product.variants))
        )
        if product is None:
            raise NotFoundError("Active product not found")
        variant = next((item for item in product.variants if item.supplier_variant_id == variant_id), None)
        if variant is None:
            if not variant_id.startswith("variant-"):
                raise BadRequestError("Invalid product variant")
            try:
                position = int(variant_id.removeprefix("variant-"))
            except ValueError as exc:
                raise BadRequestError("Invalid product variant") from exc
            variant = next((item for item in product.variants if item.position == position), None)
        if variant is None or not variant.active or variant.selling_price is None:
            raise BadRequestError("Product variant is unavailable")
        return product, variant

    @staticmethod
    def _validate_inventory(product: Product, variant: ProductVariant, quantity: int) -> None:
        if product.supplier == "printful":
            return
        available = max(0, variant.cj_inventory or 0)
        if available == 0:
            raise BadRequestError("Product variant is out of stock")
        if quantity > available:
            raise BadRequestError(f"Only {available} units are available")

    def _cart_dto(self, cart: Cart) -> CartDTO:
        items = [
            CartItemDTO(
                id=item.id,
                product_id=item.product.slug,
                variant_id=f"variant-{item.variant.position}",
                product_name=item.product.name,
                variant_name=item.variant.name or item.variant.attributes,
                quantity=item.quantity,
                unit_price=item.variant.selling_price,
                inventory=max(0, item.variant.cj_inventory or 0),
            )
            for item in cart.items
        ]
        return CartDTO(id=cart.id, items=items, subtotal=sum((item.unit_price * item.quantity for item in items), Decimal("0")))

    @staticmethod
    def _economics_snapshot(product: Product, variant: ProductVariant) -> dict:
        settings = get_settings()
        supplier_cost = variant.supplier_cost
        shipping_cost = product.shipping_cost
        missing: list[str] = []
        if supplier_cost is None:
            missing.append("historical_supplier_cost")
        if shipping_cost is None:
            missing.append("historical_shipping_cost")
        # Shipping is the existing product-level per-unit economics value; order creation never invents allocation.
        landed_cost = supplier_cost + shipping_cost if supplier_cost is not None and shipping_cost is not None else None
        return {
            "supplier_cost_inr_snapshot": supplier_cost,
            "supplier_cost_usd_snapshot": variant.supplier_cost_usd,
            "supplier_cost_currency_snapshot": "INR" if supplier_cost is not None else None,
            "shipping_cost_inr_snapshot": shipping_cost,
            "landed_cost_inr_snapshot": landed_cost,
            "pricing_fx_rate_snapshot": settings.PRICING_FX_RATE,
            "payment_gateway_policy_pct_snapshot": settings.PAYMENT_GATEWAY_PCT,
            "rto_reserve_policy_pct_snapshot": settings.RTO_RESERVE_PCT,
            "target_contribution_margin_pct_snapshot": settings.TARGET_CONTRIBUTION_MARGIN_PCT,
            "target_cac_inr_snapshot": settings.TARGET_CAC_INR,
            "economics_status": "COMPLETE" if not missing else "PARTIAL" if supplier_cost is not None or shipping_cost is not None else "UNKNOWN",
            "economics_missing": missing,
        }

    @staticmethod
    def _currency_for_country(country: str) -> str:
        return "INR" if country.strip().upper() in INDIA_COUNTRY_CODES else "USD"

    @staticmethod
    def _is_india(country: str) -> bool:
        return country.strip().upper() in INDIA_COUNTRY_CODES

    def _resolve_items(self, items: list[CartItemRequest]) -> list[tuple[Product, ProductVariant, int]]:
        return [(*self._resolve_variant(self.db, item.product_id, item.variant_id), item.quantity) for item in items]

    @staticmethod
    def _subtotal(resolved: list[tuple[Product, ProductVariant, int]]) -> Decimal:
        return sum((variant.selling_price * quantity for _, variant, quantity in resolved), Decimal("0"))

    def _shipping_quote(
        self, resolved: list[tuple[Product, ProductVariant, int]], country: str, currency: str
    ) -> tuple[str, Decimal, str | None]:
        """Single source of shipping truth for both the checkout quote and order creation."""
        shipping_service = PrintfulShippingService(self.db)
        total = Decimal("0")
        estimated = False
        applicable = False
        for product, _variant, quantity in resolved:
            if product.supplier != "printful":
                continue
            applicable = True
            try:
                estimate = shipping_service.estimate(product, country, quantity)
            except BadRequestError:
                return "UNSUPPORTED_DESTINATION", Decimal("0"), "We do not ship to this destination yet."
            except (NotFoundError, InvalidOperation, TypeError, ValueError):
                return "ERROR", Decimal("0"), "Shipping could not be calculated. Please try again."
            if estimate["status"] != "AVAILABLE":
                return "REQUIRES_VERIFICATION", Decimal("0"), estimate.get("message") or "Shipping rate requires Printful verification"
            if estimate["currency"] != currency:
                return "INVALID_CONFIGURATION", Decimal("0"), "Shipping is not configured for this destination currency."
            total += estimate["shipping_price"]
            estimated = estimated or bool(estimate.get("estimated"))
        if not applicable:
            return "NOT_APPLICABLE", Decimal("0"), None
        return "AVAILABLE", total, "Estimated shipping; pending Printful verification" if estimated else None

    def quote_order(self, user: User, payload: OrderQuoteRequest) -> OrderQuoteDTO:
        resolved = self._resolve_items(payload.items)
        subtotal = self._subtotal(resolved)
        currency = "INR"
        if not self._is_india(payload.country):
            return OrderQuoteDTO(
                currency=currency,
                subtotal=subtotal,
                shipping_amount=Decimal("0"),
                total=subtotal,
                shipping_status="UNAVAILABLE",
                shipping_message=None,
                purchasable=False,
                unavailable_reason=INTERNATIONAL_CHECKOUT_UNAVAILABLE,
            )
        status, shipping_amount, message = self._shipping_quote(resolved, payload.country, currency)
        purchasable = status in {"AVAILABLE", "NOT_APPLICABLE"}
        return OrderQuoteDTO(
            currency=currency,
            subtotal=subtotal,
            shipping_amount=shipping_amount,
            total=subtotal + shipping_amount if purchasable else subtotal,
            shipping_status=status,
            shipping_message=message,
            purchasable=purchasable,
            unavailable_reason=None if purchasable else status,
        )

    def get_cart(self, user: User) -> CartDTO:
        return self._cart_dto(self._cart(user))

    def add_cart_item(self, user: User, payload: CartItemRequest) -> CartDTO:
        cart = self._cart(user)
        product, variant = self._resolve_variant(self.db, payload.product_id, payload.variant_id)
        existing = next((item for item in cart.items if item.product_id == product.id and item.variant_id == variant.id), None)
        quantity = payload.quantity + (existing.quantity if existing else 0)
        self._validate_inventory(product, variant, quantity)
        if existing:
            existing.quantity = quantity
            existing.price_snapshot = variant.selling_price
        else:
            cart.items.append(CartItem(product=product, variant=variant, quantity=quantity, price_snapshot=variant.selling_price))
        self.db.commit()
        return self._cart_dto(self._cart(user))

    def update_cart_item(self, user: User, item_id: UUID, quantity: int) -> CartDTO:
        cart = self._cart(user)
        item = next((candidate for candidate in cart.items if candidate.id == item_id), None)
        if item is None:
            raise NotFoundError("Cart item not found")
        self._validate_inventory(item.variant, quantity)
        item.quantity = quantity
        item.price_snapshot = item.variant.selling_price
        self.db.commit()
        return self._cart_dto(self._cart(user))

    def remove_cart_item(self, user: User, item_id: UUID) -> CartDTO:
        cart = self._cart(user)
        item = next((candidate for candidate in cart.items if candidate.id == item_id), None)
        if item is None:
            raise NotFoundError("Cart item not found")
        self.db.delete(item)
        self.db.commit()
        return self._cart_dto(self._cart(user))

    def clear_cart(self, user: User) -> CartDTO:
        cart = self._cart(user)
        cart.items.clear()
        self.db.commit()
        return self._cart_dto(self._cart(user))

    def _order_dto(self, order: Order) -> OrderDTO:
        refund = next((item for item in getattr(order, "refund_requests", []) if item.status != "FAILED"), None)
        refund_message = {
            "PENDING": "Refund is being initiated.",
            "PROCESSING": "Refund is being processed. Please allow approximately 5-7 business days for LeTrusto to initiate the applicable refund where supported by the payment provider.",
            "SUCCESS": "Refund completed.",
        }.get(refund.status) if refund else None
        return OrderDTO(
            id=order.id,
            order_number=order.order_number,
            status=order.status,
            payment_status=order.payment_status,
            fulfillment_status=order.fulfillment_status,
            subtotal=order.subtotal,
            shipping_amount=order.shipping_amount,
            total=order.total,
            currency=order.currency,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            customer_phone=order.customer_phone,
            shipping_address=order.shipping_address,
            items=[
                OrderItemDTO(
                    id=item.id,
                    product_name=item.product_name,
                    product_image_url=item.product_image_url,
                    variant_name=item.variant_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.line_total,
                )
                for item in order.items
            ],
            created_at=order.created_at.isoformat(),
            payment_provider=order.payment_provider,
            paid_at=order.paid_at.isoformat() if order.paid_at else None,
            tracking_number=order.tracking_number,
            tracking_carrier=order.tracking_carrier,
            shipped_at=order.shipped_at.isoformat() if order.shipped_at else None,
            delivered_at=order.delivered_at.isoformat() if order.delivered_at else None,
            cancelled_at=order.cancelled_at.isoformat() if order.cancelled_at else None,
            cancellation_reason=order.cancellation_reason,
            refund_status=refund.status if refund else None,
            refund_amount=refund.amount if refund else None,
            refund_message=refund_message,
        )

    def create_order(self, user: User, payload: CreateOrderRequest) -> OrderDTO:
        existing = self.db.scalar(select(Order).where(Order.user_id == user.id, Order.idempotency_key == payload.idempotency_key).options(selectinload(Order.items)))
        if existing:
            return self._order_dto(existing)
        if not self._is_india(payload.shipping_address.country):
            raise BadRequestError("Orders can currently be placed only for delivery addresses in India.")
        resolved = self._resolve_items(payload.items)
        locked_variants = list(self.db.scalars(
            select(ProductVariant)
            .where(ProductVariant.id.in_([variant.id for _, variant, _ in resolved]))
            .order_by(ProductVariant.id)
            .with_for_update()
        ).all())
        variants_by_id = {variant.id: variant for variant in locked_variants}
        if len(variants_by_id) != len({variant.id for _, variant, _ in resolved}):
            raise BadRequestError("Product variant is unavailable")
        resolved = [(product, variants_by_id[variant.id], quantity) for product, variant, quantity in resolved]
        for product, variant, quantity in resolved:
            self._validate_inventory(product, variant, quantity)
        currency = self._currency_for_country(payload.shipping_address.country)
        shipping_status, shipping_amount, _ = self._shipping_quote(resolved, payload.shipping_address.country, currency)
        if shipping_status not in {"AVAILABLE", "NOT_APPLICABLE"}:
            self.db.rollback()
            raise BadRequestError("Shipping to this destination is currently unavailable.")
        for product, variant, quantity in resolved:
            try:
                preflight = asyncio.run(self.fulfillment_preflight_service.check(
                    product_id=product.id,
                    variant_id=variant.id,
                    quantity=quantity,
                    destination_country=payload.shipping_address.country,
                ))
            except Exception as exc:
                self.db.rollback()
                raise BadRequestError("Product variant is unavailable for the selected destination") from exc
            if preflight.status != "FULFILLABLE":
                self.db.rollback()
                raise BadRequestError("Product variant is unavailable for the selected destination")
        subtotal = self._subtotal(resolved)
        now = datetime.now(timezone.utc)
        order = Order(
            order_number=f"LT-{now.strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}",
            user_id=user.id,
            status="PENDING_PAYMENT",
            payment_status="PENDING",
            fulfillment_status="PENDING",
            subtotal=subtotal,
            shipping_amount=shipping_amount,
            total=subtotal + shipping_amount,
            currency=currency,
            customer_name=payload.customer.name,
            customer_email=str(payload.customer.email),
            customer_phone=payload.customer.phone,
            shipping_address=payload.shipping_address.model_dump(),
            idempotency_key=payload.idempotency_key,
        )
        order.items = [
            OrderItem(product_id=product.id, variant_id=variant.id, product_name=product.name, product_image_url=product.images[0].url if product.images else None, variant_name=variant.name or variant.attributes, quantity=quantity, unit_price=variant.selling_price, line_total=variant.selling_price * quantity, **self._economics_snapshot(product, variant))
            for product, variant, quantity in resolved
        ]
        try:
            self.db.add(order)
            self.db.flush()
            InventoryReservationService(self.db).reserve_order(order, variants_by_id)
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            if isinstance(exc, IntegrityError):
                existing = self.db.scalar(select(Order).where(Order.user_id == user.id, Order.idempotency_key == payload.idempotency_key).options(selectinload(Order.items), selectinload(Order.refund_requests)))
                if existing:
                    return self._order_dto(existing)
            raise
        self.db.refresh(order)
        return self._order_dto(order)

    def get_order(self, user: User, order_id: UUID) -> OrderDTO:
        order = self.db.scalar(select(Order).where(Order.id == order_id, Order.user_id == user.id).options(selectinload(Order.items), selectinload(Order.refund_requests)))
        if order is None:
            raise NotFoundError("Order not found")
        return self._order_dto(order)

    def list_orders(self, user: User, page: int = 1, page_size: int = 20) -> OrderListDTO:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 20)
        base = select(Order).where(Order.user_id == user.id)
        total = self.db.scalar(select(func.count()).select_from(base.subquery())) or 0
        orders = list(self.db.scalars(
            base.options(selectinload(Order.items), selectinload(Order.refund_requests))
            .order_by(Order.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all())
        return OrderListDTO(
            items=[self._order_dto(order) for order in orders],
            page=page,
            page_size=page_size,
            total=total,
            has_next=page * page_size < total,
        )