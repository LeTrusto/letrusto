from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.core.security import create_access_token
from app.models.entities import InventoryReservation, MarketingSpend, Order, OrderItem, OrderMarketingAttribution, PaymentAttempt, Product, ProductVariant, RefundRequest, User
from app.schemas.orders import CartItemRequest, CreateOrderRequest, CustomerDetails, ShippingAddress
from app.services.admin_analytics_service import AdminAnalyticsService
from app.services.order_service import OrderService


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
        assert summary.cac.status == "NOT_CONFIGURED"
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


def test_new_order_captures_immutable_economics_snapshot():
    db = SessionLocal()
    suffix = uuid4().hex[:8]
    user = User(email=f"snapshot-{suffix}@example.com", full_name="Snapshot Test")
    product = Product(slug=f"snapshot-{suffix}", name="Snapshot Product", description="test", status="ACTIVE", supplier="cj", supplier_product_id=f"CJ-{suffix}", price_value=Decimal("100"), selling_price=Decimal("100"), shipping_cost=Decimal("12"), ai_score=1, rating=Decimal("1"), ai_summary="", review_summary="")
    variant = ProductVariant(product=product, supplier_variant_id=f"VID-{suffix}", supplier_variant_sku=f"SKU-{suffix}", name="Default", position=1, selling_price=Decimal("100"), supplier_cost=Decimal("40"), supplier_cost_usd=Decimal("0.50"), cj_inventory=5, active=True)
    db.add_all([user, product, variant])
    db.commit()
    try:
        request = CreateOrderRequest(items=[CartItemRequest(product_id=product.slug, variant_id="variant-1", quantity=2)], customer=CustomerDetails(name="Snapshot Test", email=user.email, phone="9876543210"), shipping_address=ShippingAddress(address="1 Test", city="Bengaluru", state="Karnataka", postal_code="560001", country="IN"), idempotency_key=f"snapshot-{suffix}-key")
        result = OrderService(db).create_order(user, request)
        item = db.query(OrderItem).filter(OrderItem.order_id == result.id).one()
        assert item.supplier_cost_inr_snapshot == Decimal("40")
        assert item.supplier_cost_usd_snapshot == Decimal("0.5000")
        assert item.shipping_cost_inr_snapshot == Decimal("12")
        assert item.landed_cost_inr_snapshot == Decimal("52")
        assert item.economics_status == "COMPLETE"
        order = db.get(Order, result.id)
        order.status = "PAID"
        order.payment_status = "PAID"
        order.paid_at = datetime.now(timezone.utc)
        db.commit()
        period = AdminAnalyticsService.resolve_period("today")
        summary = AdminAnalyticsService(db).summary(period)
        assert summary.contribution_before_cac.value == Decimal("96.00")
        assert summary.contribution_status == "PARTIAL"
        assert summary.contribution_margin_percent == Decimal("48.00")
        original = (item.supplier_cost_inr_snapshot, item.shipping_cost_inr_snapshot, item.landed_cost_inr_snapshot)
        variant.supplier_cost = Decimal("999")
        product.shipping_cost = Decimal("999")
        db.commit()
        db.expire(item)
        assert (item.supplier_cost_inr_snapshot, item.shipping_cost_inr_snapshot, item.landed_cost_inr_snapshot) == original
    finally:
        cleanup(db, user, product)


def test_existing_order_without_snapshot_remains_unknown():
    db = SessionLocal()
    existing = db.query(Order).filter(Order.order_number == "LT-20260818-CE79A428").one()
    try:
        assert existing.items[0].supplier_cost_inr_snapshot is None
        assert existing.items[0].shipping_cost_inr_snapshot is None
        assert existing.items[0].economics_status is None
    finally:
        db.close()


def test_export_allocates_refund_once_across_multiple_items():
    db = SessionLocal()
    user, product, order, refund, reservation = fixture(db)
    second = OrderItem(order=order, product=product, variant=order.items[0].variant, product_name="Second historical item", variant_name="Silver", quantity=1, unit_price=Decimal("100"), line_total=Decimal("100"))
    order.total = Decimal("200")
    order.subtotal = Decimal("200")
    db.add(second)
    db.commit()
    try:
        period = AdminAnalyticsService.resolve_period("custom", order.created_at.date(), order.created_at.date())
        rows = AdminAnalyticsService(db).export_rows(period)
        assert sum((row.refund_amount or Decimal("0") for row in rows if row.order_number == order.order_number), Decimal("0")) == Decimal("10.00")
    finally:
        cleanup(db, user, product)


def test_attributed_cac_updates_order_product_variant_and_summary_without_using_target_cac():
    db = SessionLocal()
    user, product, order, refund, reservation = fixture(db)
    spend = None
    try:
        item = order.items[0]
        item.supplier_cost_inr_snapshot = Decimal("40")
        item.shipping_cost_inr_snapshot = Decimal("10")
        spend = MarketingSpend(spend_date=order.paid_at.date(), channel="META", campaign="fixture", spend_amount=Decimal("20"), currency="INR")
        attribution = OrderMarketingAttribution(order_id=order.id, channel="META", campaign="fixture", attribution_method="test", status="ATTRIBUTED")
        db.add_all([spend, attribution])
        db.commit()
        period = AdminAnalyticsService.resolve_period("custom", order.paid_at.date(), order.paid_at.date())
        service = AdminAnalyticsService(db)
        order_profit = service.order_profitability(order.id)
        assert order_profit.contribution_before_cac.value == Decimal("40.00")
        assert order_profit.actual_cac.value == Decimal("20.00")
        assert order_profit.contribution_after_cac.value == Decimal("20.00")
        assert order_profit.cac_status == "ATTRIBUTED"
        summary = service.summary(period)
        assert summary.marketing_spend == Decimal("20.00")
        assert summary.attributed_cac.value == Decimal("20.00")
        assert summary.blended_cac.value == Decimal("20.00")
        assert summary.contribution_after_cac.value == Decimal("20.00")
        assert summary.roas.value == Decimal("5.00")
        product_row = service.product_performance(period)[0]
        variant_row = service.variant_performance(period)[0]
        assert product_row.actual_cac.value == Decimal("20.00")
        assert product_row.contribution_after_cac.value == Decimal("20.00")
        assert variant_row.actual_cac.value == Decimal("20.00")
        assert variant_row.contribution_after_cac.value == Decimal("20.00")
    finally:
        if spend is not None:
            db.delete(spend)
            db.commit()
        cleanup(db, user, product)


def test_non_attributed_product_and_variant_do_not_receive_blended_cac():
    db = SessionLocal()
    user, product, order, refund, reservation = fixture(db)
    spend = None
    try:
        spend = MarketingSpend(spend_date=order.paid_at.date(), channel="META", campaign="unattributed", spend_amount=Decimal("150"), currency="INR")
        db.add(spend)
        db.commit()
        period = AdminAnalyticsService.resolve_period("custom", order.paid_at.date(), order.paid_at.date())
        service = AdminAnalyticsService(db)
        assert service.summary(period).blended_cac.value == Decimal("150.00")
        product_row = service.product_performance(period)[0]
        variant_row = service.variant_performance(period)[0]
        assert product_row.actual_cac.value is None and product_row.cac_status == "NOT_ATTRIBUTED"
        assert variant_row.actual_cac.value is None and variant_row.cac_status == "NOT_ATTRIBUTED"
        order_profit = service.order_profitability(order.id)
        assert order_profit.actual_cac.value is None
        assert order_profit.cac_status == "NOT_ATTRIBUTED"
    finally:
        if spend is not None:
            db.delete(spend)
            db.commit()
        cleanup(db, user, product)


def test_analytics_financial_endpoints_require_admin_role():
    db = SessionLocal()
    suffix = uuid4().hex[:8]
    customer = User(email=f"customer-{suffix}@example.com", full_name="Customer")
    admin = User(email=f"admin-{suffix}@example.com", full_name="Admin", role="admin")
    db.add_all([customer, admin])
    db.commit()
    try:
        client = TestClient(app)
        assert client.get("/api/v1/admin/analytics/summary").status_code == 401
        customer_token = create_access_token(str(customer.id))
        assert client.get("/api/v1/admin/analytics/summary", headers={"Authorization": f"Bearer {customer_token}"}).status_code == 401
        admin_token = create_access_token(str(admin.id))
        assert client.get("/api/v1/admin/analytics/summary", headers={"Authorization": f"Bearer {admin_token}"}).status_code == 200
    finally:
        db.delete(customer)
        db.delete(admin)
        db.commit()
        db.close()
