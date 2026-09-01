import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models.entities import OperationalAlertState, Product, ProductVariant
from app.services.email_service import EmailDeliveryError
from app.services.operational_alert_service import OperationalAlertService
from app.db.session import SessionLocal


class FakeEmail:
    def __init__(self, *, failure=None):
        self.sent = []
        self.failure = failure

    def send_template(self, template, **kwargs):
        if self.failure:
            raise self.failure
        self.sent.append((template, kwargs))


def make_product(db, *, supplier="cj", stock=10):
    product = Product(
        id=uuid4(), slug=f"alert-{uuid4()}", name="Alert product", description="Test product",
        status="ACTIVE", supplier=supplier, supplier_product_id="supplier-product",
    )
    variant = ProductVariant(
        id=uuid4(), product_id=product.id, supplier_variant_id="variant-1", supplier_variant_sku="SKU-1",
        name="Blue", position=1, active=True, cj_inventory=stock, total_inventory=stock,
    )
    db.add_all([product, variant])
    db.commit()
    return product, variant


def cleanup(db, product_id):
    db.query(OperationalAlertState).delete(synchronize_session=False)
    db.query(Product).filter(Product.id == product_id).delete(synchronize_session=False)
    db.commit()
    db.close()


def test_low_stock_alerts_on_transition_suppresses_repeat_and_alerts_again_after_recovery():
    db = SessionLocal()
    product, variant = make_product(db, stock=10)
    email = FakeEmail()
    service = OperationalAlertService(db, email_service=email)
    service.threshold = 5
    now = datetime.now(timezone.utc)
    try:
        service.evaluate_low_stock(now)
        initial_alerts = len(email.sent)
        variant.cj_inventory = 5
        db.commit()
        service.evaluate_low_stock(now + timedelta(minutes=1))
        assert len(email.sent) == initial_alerts + 1
        before_repeat = len(email.sent)
        service.evaluate_low_stock(now + timedelta(minutes=2))
        assert len(email.sent) == before_repeat
        variant.cj_inventory = 6
        db.commit()
        assert service.evaluate_low_stock(now + timedelta(minutes=3))["recovered"] == 1
        variant.cj_inventory = 2
        db.commit()
        before_second_transition = len(email.sent)
        service.evaluate_low_stock(now + timedelta(minutes=4))
        assert len(email.sent) == before_second_transition + 1
        assert any("SKU-1" in item[1]["context"]["details"][1][1] for item in email.sent)
    finally:
        cleanup(db, product.id)


def test_printful_products_do_not_generate_low_stock_alerts():
    db = SessionLocal()
    product, _ = make_product(db, supplier="printful", stock=0)
    email = FakeEmail()
    try:
        result = OperationalAlertService(db, email_service=email).evaluate_low_stock()
        assert result["sent"] >= 0
        assert all(
            ("Product", "Alert product") not in item[1]["context"]["details"]
            for item in email.sent
        )
    finally:
        cleanup(db, product.id)


def test_sync_failure_alert_cooldown_and_recovery():
    db = SessionLocal()
    email = FakeEmail()
    service = OperationalAlertService(db, email_service=email)
    service.cooldown = timedelta(minutes=60)
    failure = [{"product_id": str(uuid4()), "category": "TimeoutError"}]
    now = datetime.now(timezone.utc)
    try:
        assert service.process_inventory_sync_failures(failure, now)["sent"] == 1
        assert service.process_inventory_sync_failures(failure, now + timedelta(minutes=15))["suppressed"] == 1
        assert service.process_inventory_sync_failures([], now + timedelta(minutes=16))["recovered"] == 1
        assert service.process_inventory_sync_failures(failure, now + timedelta(minutes=61))["sent"] == 1
        assert len(email.sent) == 2
    finally:
        db.query(OperationalAlertState).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_email_failure_is_recorded_without_raising_or_leaking_exception_text(caplog):
    db = SessionLocal()
    email = FakeEmail(failure=EmailDeliveryError("secret-resend-key"))
    service = OperationalAlertService(db, email_service=email)
    try:
        result = service.process_inventory_sync_failures([{"product_id": str(uuid4()), "category": "HTTPError"}])
        state = db.query(OperationalAlertState).filter_by(alert_type="INVENTORY_SYNC_FAILURE", alert_key="cj").one()
        assert result["delivery_failures"] == 1
        assert state.delivery_failure_reason == "EmailDeliveryError"
        assert "secret-resend-key" not in caplog.text
    finally:
        db.query(OperationalAlertState).delete(synchronize_session=False)
        db.commit()
        db.close()