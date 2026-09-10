from fastapi import status
from fastapi.testclient import TestClient

from tests.plugins.factories import Factory


def test_get_taxes(factory: Factory, client: TestClient) -> None:
    taxes_count = 3
    store = factory.stores.create_one()
    factory.taxes.create_many(taxes_count, store=store)

    response = client.get("/api/taxes")

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert len(result["items"]) == taxes_count


def test_get_taxes_by_store(factory: Factory, client: TestClient) -> None:
    taxes_count = 3
    store = factory.stores.create_one()
    factory.taxes.create_many(taxes_count, store=store)
    factory.taxes.create_many(2)

    response = client.get("/api/taxes", params={"store": str(store.slug)})

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert len(result["items"]) == taxes_count


def test_get_taxes_store_not_found(client: TestClient) -> None:
    response = client.get("/api/taxes", params={"store": "store"})

    assert response.status_code == status.HTTP_404_NOT_FOUND
