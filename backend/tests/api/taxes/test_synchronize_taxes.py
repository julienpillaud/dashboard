from cleanstack.mongo import MongoDocument
from fastapi import status
from fastapi.testclient import TestClient
from pymongo.synchronous.database import Database

from tests.factories.factory import Factory
from tests.fakes.pos_manager import FakePOSManager


def test_sync_taxes(
    factory: Factory,
    fake_pos_manager: FakePOSManager,
    client: TestClient,
) -> None:
    taxes_count = 3
    store = factory.stores.create_one()
    taxes = factory.taxes.create_many(taxes_count, store=store)
    fake_pos_manager.add_taxes(taxes=[tax.raw for tax in taxes])

    response = client.post("/api/taxes/synchronize", params={"store": str(store.slug)})

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["metrics"]["pos_total"] == taxes_count
    assert result["metrics"]["db_before"] == taxes_count
    assert result["summary"]["created"] == 0
    assert result["summary"]["updated"] == 0
    assert result["summary"]["deleted"] == 0


def test_sync_taxes_to_create(
    factory: Factory,
    fake_pos_manager: FakePOSManager,
    client: TestClient,
    database: Database[MongoDocument],
) -> None:
    taxes_count = 3
    store = factory.stores.create_one()
    pos_taxes = factory.taxes.create_many(taxes_count - 1, store=store)
    tax_to_create = factory.taxes.build(store=store)
    fake_pos_manager.add_taxes(taxes=[tax.raw for tax in [*pos_taxes, tax_to_create]])

    response = client.post(
        "/api/taxes/synchronize",
        params={"store": str(store.slug), "dry_run": False},
    )

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["metrics"]["pos_total"] == taxes_count
    assert result["metrics"]["db_before"] == taxes_count - 1
    assert result["summary"]["created"] == 1
    assert result["summary"]["updated"] == 0
    assert result["summary"]["deleted"] == 0

    db_taxes = database["taxes"].find({"store_id": store.id}).to_list()
    assert len(db_taxes) == taxes_count
