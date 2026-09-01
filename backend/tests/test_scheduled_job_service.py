import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services.catalog_inventory_sync_service import CatalogInventorySyncService
from app.services.scheduled_job_service import ScheduledJobRunner


class FakeResult:
    def __init__(self, value):
        self.value = value

    def scalar(self):
        return self.value


class FakeConnection:
    def __init__(self, acquired=True):
        self.acquired = acquired
        self.lock_queries = 0

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, *_args, **_kwargs):
        self.lock_queries += 1
        return FakeResult(self.acquired)


class FakeEngine:
    def __init__(self, acquired=True):
        self.connection = FakeConnection(acquired)

    def connect(self):
        return self.connection


class FakeSession:
    def __init__(self):
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def rollback(self):
        self.rolled_back = True


class FakeSessionFactory:
    def __init__(self):
        self.session = FakeSession()

    def __call__(self, **kwargs):
        assert "bind" in kwargs
        return self.session


class FakeReconciliation:
    calls = 0

    def __init__(self, db):
        self.db = db
        type(self).calls += 1

    async def run_order_lifecycle_reconciliation(self):
        self.calls += 1
        return SimpleNamespace(failures=[], model_dump=lambda mode: {"failures": []})


class FakeInventory:
    calls = 0

    def __init__(self, db):
        self.db = db
        type(self).calls += 1

    async def sync_active_products(self):
        return {"supplier": "cj", "attempted": 2, "synced": 2, "failed": 0, "failures": []}


def test_scheduler_runs_inventory_then_existing_reconciliation(monkeypatch):
    engine = FakeEngine()
    sessions = FakeSessionFactory()
    FakeInventory.calls = 0
    FakeReconciliation.calls = 0
    monkeypatch.setattr("app.services.scheduled_job_service.CatalogInventorySyncService", FakeInventory)
    monkeypatch.setattr("app.services.scheduled_job_service.OrderLifecycleReconciliationService", FakeReconciliation)

    result = asyncio.run(ScheduledJobRunner(db_engine=engine, db_session_factory=sessions, lock_key=10).run_once())

    assert result["status"] == "SUCCEEDED"
    assert result["inventory"]["supplier"] == "cj"
    assert FakeInventory.calls == 1
    assert FakeReconciliation.calls == 1
    assert engine.connection.lock_queries == 1


def test_scheduler_skips_overlapping_run_without_touching_services(monkeypatch):
    engine = FakeEngine(acquired=False)
    sessions = FakeSessionFactory()
    monkeypatch.setattr("app.services.scheduled_job_service.CatalogInventorySyncService", lambda _: pytest.fail("inventory should not run"))
    monkeypatch.setattr("app.services.scheduled_job_service.OrderLifecycleReconciliationService", lambda _: pytest.fail("reconciliation should not run"))

    result = asyncio.run(ScheduledJobRunner(db_engine=engine, db_session_factory=sessions, lock_key=10).run_once())

    assert result["status"] == "SKIPPED_OVERLAPPING"
    assert engine.connection.lock_queries == 1


def test_scheduler_reports_partial_inventory_failure_without_hiding_it(monkeypatch):
    engine = FakeEngine()
    sessions = FakeSessionFactory()

    class PartialInventory(FakeInventory):
        async def sync_active_products(self):
            return {"supplier": "cj", "attempted": 2, "synced": 1, "failed": 1, "failures": [{"product_id": str(uuid4()), "category": "TimeoutException"}]}

    monkeypatch.setattr("app.services.scheduled_job_service.CatalogInventorySyncService", PartialInventory)
    monkeypatch.setattr("app.services.scheduled_job_service.OrderLifecycleReconciliationService", FakeReconciliation)

    result = asyncio.run(ScheduledJobRunner(db_engine=engine, db_session_factory=sessions, lock_key=10).run_once())

    assert result["status"] == "PARTIAL_FAILURE"
    assert result["inventory"]["failed"] == 1
    assert result["inventory"]["failures"][0]["category"] == "TimeoutException"


def test_scheduler_rolls_back_and_propagates_database_failure(monkeypatch):
    engine = FakeEngine()
    sessions = FakeSessionFactory()

    class BrokenInventory:
        def __init__(self, db):
            pass

        async def sync_active_products(self):
            raise RuntimeError("database connection failed")

    monkeypatch.setattr("app.services.scheduled_job_service.CatalogInventorySyncService", BrokenInventory)

    with pytest.raises(RuntimeError, match="database connection failed"):
        asyncio.run(ScheduledJobRunner(db_engine=engine, db_session_factory=sessions, lock_key=10).run_once())
    assert sessions.session.rolled_back is True


def test_catalog_inventory_sync_query_is_cj_only_and_retries_after_partial_failure(monkeypatch):
    class ScalarResult:
        def all(self):
            return [SimpleNamespace(id=uuid4()), SimpleNamespace(id=uuid4())]

    class FakeDb:
        def __init__(self):
            self.statement = None
            self.rollbacks = 0

        def scalars(self, statement):
            self.statement = statement
            return ScalarResult()

        def rollback(self):
            self.rollbacks += 1

    db = FakeDb()
    service = CatalogInventorySyncService(db)
    calls = []

    async def sync(product_id):
        calls.append(product_id)
        if len(calls) == 1:
            raise TimeoutError("supplier timeout")

    service.products.sync_inventory = sync
    result = asyncio.run(service.sync_active_products())

    sql = str(db.statement)
    assert "products.supplier =" in sql
    assert result["supplier"] == "cj"
    assert result["attempted"] == 2
    assert result["synced"] == 1
    assert result["failed"] == 1
    assert db.rollbacks == 1
    assert len(calls) == 2
