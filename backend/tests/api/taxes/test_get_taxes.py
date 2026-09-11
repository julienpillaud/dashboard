from fastapi import status
from fastapi.testclient import TestClient

from tests.plugins.factories import Factory


def test_get_taxes(factory: Factory, client: TestClient) -> None:
    taxes_count = 3
    factory.taxes.create_many(taxes_count)

    response = client.get("/api/taxes")

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert len(result["items"]) == taxes_count
