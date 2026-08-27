import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.infrastructure.tactill.data import CATEGORIES


@pytest.mark.local_test
def test_get_articles(client: TestClient) -> None:
    article_name = "Kwak 33cL"
    params = {"filter": f"raw.name={article_name}"}
    response = client.get("/api/articles", params=params)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()

    article = result["items"][0]
    assert article["raw"]["name"] == article_name


@pytest.mark.parametrize("category", CATEGORIES)
@pytest.mark.parametrize("store", ["angouleme", "sainte-eulalie", "pessac"])
@pytest.mark.local_test
def test_get_articles_by_category(
    client: TestClient,
    store: str,
    category: str,
) -> None:
    params = {"store": store, "filter": f"category={category}", "size": 1000}
    response = client.get("/api/articles", params=params)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    for article in result["items"]:
        assert article["category"] == category
