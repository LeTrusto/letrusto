from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.entities import Cart, CartItem, Order, OrderItem, Product, ProductVariant, User
from app.schemas.orders import CartDTO, CartItemDTO, CartItemRequest, CreateOrderRequest, OrderDTO, OrderItemDTO


class OrderService:
    def __init__(self, db: Session) -> None:
        self.db = db

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
    def _validate_inventory(variant: ProductVariant, quantity: int) -> None:
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

    def get_cart(self, user: User) -> CartDTO:
        return self._cart_dto(self._cart(user))

    def add_cart_item(self, user: User, payload: CartItemRequest) -> CartDTO:
        cart = self._cart(user)
        product, variant = self._resolve_variant(self.db, payload.product_id, payload.variant_id)
        existing = next((item for item in cart.items if item.product_id == product.id and item.variant_id == variant.id), None)
        quantity = payload.quantity + (existing.quantity if existing else 0)
        self._validate_inventory(variant, quantity)
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
        )

    def create_order(self, user: User, payload: CreateOrderRequest) -> OrderDTO:
        existing = self.db.scalar(select(Order).where(Order.user_id == user.id, Order.idempotency_key == payload.idempotency_key).options(selectinload(Order.items)))
        if existing:
            return self._order_dto(existing)
        resolved: list[tuple[Product, ProductVariant, int]] = []
        for item in payload.items:
            product, variant = self._resolve_variant(self.db, item.product_id, item.variant_id)
            self._validate_inventory(variant, item.quantity)
            resolved.append((product, variant, item.quantity))
        subtotal = sum((variant.selling_price * quantity for _, variant, quantity in resolved), Decimal("0"))
        now = datetime.now(timezone.utc)
        order = Order(
            order_number=f"LT-{now.strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}",
            user_id=user.id,
            status="PENDING_PAYMENT",
            payment_status="PENDING",
            fulfillment_status="PENDING",
            subtotal=subtotal,
            shipping_amount=Decimal("0"),
            total=subtotal,
            customer_name=payload.customer.name,
            customer_email=str(payload.customer.email),
            customer_phone=payload.customer.phone,
            shipping_address=payload.shipping_address.model_dump(),
            idempotency_key=payload.idempotency_key,
        )
        order.items = [
            OrderItem(product_id=product.id, variant_id=variant.id, product_name=product.name, variant_name=variant.name or variant.attributes, quantity=quantity, unit_price=variant.selling_price, line_total=variant.selling_price * quantity)
            for product, variant, quantity in resolved
        ]
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return self._order_dto(order)

    def get_order(self, user: User, order_id: UUID) -> OrderDTO:
        order = self.db.scalar(select(Order).where(Order.id == order_id, Order.user_id == user.id).options(selectinload(Order.items)))
        if order is None:
            raise NotFoundError("Order not found")
        return self._order_dto(order)