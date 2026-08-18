import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.order_reconciliation_service import OrderLifecycleReconciliationService


def service(monkeypatch):
    monkeypatch.setattr(
        "app.services.order_reconciliation_service.get_settings",
        lambda: SimpleNamespace(
            ORDER_RECONCILIATION_ENABLED=True,
            PENDING_PAYMENT_RECONCILIATION_AGE_MINUTES=30,
            RECONCILIATION_BATCH_SIZE=50,
            CJ_API_KEY="",
        ),
    )
    return OrderLifecycleReconciliationService(MagicMock())


def test_orchestrator_runs_all_steps_when_each_succeeds(monkeypatch):
    reconciliation = service(monkeypatch)
    calls = []
    reconciliation.expire_reservations = lambda: calls.append("reservations") or 2
    async def payments(failures, unavailable):
        calls.append("payments")
        return 3
    async def fulfillment(failures, unavailable):
        calls.append("fulfillment")
        return 4
    async def tracking(failures, unavailable):
        calls.append("tracking")
        return 5
    reconciliation.reconcile_pending_payments = payments
    reconciliation.reconcile_fulfillment = fulfillment
    reconciliation.sync_tracking = tracking
    reconciliation.detect_inconsistencies = lambda: []

    result = asyncio.run(reconciliation.run_order_lifecycle_reconciliation())

    assert calls == ["reservations", "payments", "fulfillment", "tracking"]
    assert result.reservations_expired == 2
    assert result.payments_reconciled == 3
    assert result.fulfillment_submitted == 4
    assert result.tracking_synced == 5
    assert result.failures == []


def test_orchestrator_continues_after_one_job_fails(monkeypatch):
    reconciliation = service(monkeypatch)
    calls = []
    reconciliation.expire_reservations = lambda: (_ for _ in ()).throw(RuntimeError("expired failed"))
    async def payments(failures, unavailable):
        calls.append("payments")
        return 1
    async def fulfillment(failures, unavailable):
        calls.append("fulfillment")
        return 1
    async def tracking(failures, unavailable):
        calls.append("tracking")
        return 1
    reconciliation.reconcile_pending_payments = payments
    reconciliation.reconcile_fulfillment = fulfillment
    reconciliation.sync_tracking = tracking
    reconciliation.detect_inconsistencies = lambda: []

    result = asyncio.run(reconciliation.run_order_lifecycle_reconciliation())

    assert calls == ["payments", "fulfillment", "tracking"]
    assert result.failures == ["reservations:expired failed"]


def test_provider_unavailable_is_reported_without_failure(monkeypatch):
    reconciliation = service(monkeypatch)
    reconciliation.expire_reservations = lambda: 0
    async def payments(failures, unavailable):
        unavailable.append("payment:provider")
        return 0
    async def fulfillment(failures, unavailable):
        unavailable.append("fulfillment:provider")
        return 0
    async def tracking(failures, unavailable):
        unavailable.append("tracking:provider")
        return 0
    reconciliation.reconcile_pending_payments = payments
    reconciliation.reconcile_fulfillment = fulfillment
    reconciliation.sync_tracking = tracking
    reconciliation.detect_inconsistencies = lambda: []

    result = asyncio.run(reconciliation.run_order_lifecycle_reconciliation())

    assert result.failures == []
    assert result.provider_unavailable == ["payment:provider", "fulfillment:provider", "tracking:provider"]