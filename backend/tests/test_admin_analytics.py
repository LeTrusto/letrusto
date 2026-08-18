from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.entities import InventoryReservation, Order, OrderItem, PaymentAttempt, Product, ProductVariant, RefundRequest, User
from app.services.admin_analytics_service import AdminAnalyticsService


def fixture(db):
    suffix = uuid4().hex[:8]
    now = datetime.now(timezone.utc) - timedelta(days=60)
    user = User(email=f"analytics-{suffix}@example.com", full_name="Analytics Test")
    product = Product(slug=f"analytics-{suffix}", name="Analytics Fixture", description="test", status="ACTIVE", supplier="cj", supplier_product_id=f"CJ-{suffix}", price_value=Decimal("100"), selling_price=Decimal("100"), cj_inventory=5, factory_inventory=999, ai_score=1, rating=Decimal("1"), ai_summary="", review_summary="")
    variant = ProductVariant(product=product, supplier_variant_id=f"VID-{suffix}", supplier_variant_sku=f"SKU-{suffix}", name="Gold", position=1, selling_price=Decimal("100"), cj_inventory=5, factory_inventory=999, active=True)
    order = Order(order_number=f"LT-AN-{suffix}", user=user, status="PAID", payment_status="PAID", fulfillment_status="PENDING", subtotal=Decimal("100"), shipping_amount=Decimal("0"), total=Decimal("100"), currency="INR", customer_name="Analytics Test", customer_email=user.email, customer_phone="9876543210", shipping_address={"address":"1 Test","city":"Bengaluru","state":"Karnataka","postal_code":"560001","country":"IN"}, idempotency_key=f"analytics-{suffix}", paid_at=now, created_at=now, items=[OrderItem(product=product, variant=variant, product_name="Historical Analytics Fixture", product_image_url=None, variant_name="Gold", quantity=1, unit_price=Decimal("100"), line_total=Decimal("100"))])
    db.add_all([user, product, variant, order])
    db.commit()
    refund = RefundRequest(order=order, provider="CASHFREE", provider_order_id=f"cf-{suffix}", provider_refund_id=f"rf-{suffix}", amount=Decimal("10"), currency="INR", status="SUCCESS", idempotency_key=f"refund-{suffix}", requested_by="test", completed_at=now)
    reservation = InventoryReservation(order=order, order_item=order.items[0], variant=variant, quantity=2, status="ACTIVE", expires_at=datetime.now(timezone.utc) + timedelta(minutes=10))
    db.add_all([refund, reservation])
    db.commit()
    return user, product, order, refund, reservation


def cleanup(db, user, product):
    db.query(InventoryReservation).filter(InventoryReservation.order_id.in_(db.query(Order.id).filter(Order.user_id == user.id))).delete(synchronize_session=False)
    db.query(RefundRequest).filter(RefundRequest.order_id.in_(db.query(Order.id).filter(Order.user_id == user.id))).delete(synchronize_session=False)
    db.query(PaymentAttempt).filter(PaymentAttempt.order_id.in_(db.query(Order.id).filter(Order.user_id == user.id))).delete(synchronize_session=False)
    db.query(OrderItem).filter(OrderItem.order_id.in_(db.query(Order.id).filter(Order.user_id == user.id))).delete(synchronize_session=False)
    db.query(Order).filter(Order.user_id == user.id).delete(synchronize_session=False)
    db.delete(user)
    db.delete(product)
    db.commit()
    db.close()


def test_summary_distinguishes_actuals_from_unknown_costs():
    db = SessionLocal()
    user, product, order, refund, reservation = fixture(db)
    try:
        period = AdminAnalyticsService.resolve_period("custom", order.created_at.date(), order.created_at.date())
        summary = AdminAnalyticsService(db).summary(period)
        assert summary.gross_order_value == Decimal("100.00")
        assert summary.paid_sales == Decimal("100.00")
        assert summary.refunded_amount == Decimal("10.00")
        assert summary.net_sales == Decimal("90.00")
        assert summary.landed_cost.value is None
        assert summary.payment_fees.status == "NOT_AVAILABLE"
        assert summary.cac.status == "NOT_AVAILABLE"
        assert summary.policy_assumptions["target_cac_inr"] == Decimal("150.00")
    finally:
        cleanup(db, user, product)


def test_product_and_inventory_reporting_use_snapshots_and_cj_only():
    db = SessionLocal()
    user, product, order, refund, reservation = fixture(db)
    try:
        period = AdminAnalyticsService.resolve_period("custom", order.created_at.date(), order.created_at.date())
        performance = AdminAnalyticsService(db).product_performance(period)
        assert performance[0].product_name == "Historical Analytics Fixture"
        assert performance[0].net_sales == Decimal("90.00")
        assert performance[0].landed_cost.value is None
        inventory = AdminAnalyticsService(db).inventory()
        row = next(item for item in inventory if item.product_id == product.id)
        assert row.cj_inventory == 5
        assert row.factory_inventory == 999
        assert row.active_reservations == 2
        assert row.available_customer_inventory == 3
    finally:
        cleanup(db, user, product)


def test_analytics_requires_admin_authentication():
    response = TestClient(app).get("/api/v1/admin/analytics/summary")
    assert response.status_code == 401
