import uuid

from fastapi import status
from fastapi.testclient import TestClient

from app.domain.articles.entities import ArticleInput
from tests.factories.factory import Factory
from tests.mocks.pos_manager import FakePOSManager


def test_create_article(
    factory: Factory,
    tokens: None,
    client: TestClient,
    fake_pos_manager: FakePOSManager,
) -> None:
    data = factory.articles.build()
    article_input = ArticleInput(
        name=data.name,
        category=data.category,
        total_cost=data.total_cost,
        tax_rate=data.tax_rate,
        distributor=data.distributor,
        details=data.details,
        prices={
            uuid.UUID(store_id): pos_article.price
            for store_id, pos_article in data.store_mapping.items()
        },
    )

    response = client.post("/api/articles", json=article_input.model_dump(mode="json"))

    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert result["name"] == article_input.name
    assert result["category"] == article_input.category
    assert result["total_cost"] == float(article_input.total_cost)
    assert result["tax_rate"] == article_input.tax_rate
    assert result["distributor"] == article_input.distributor

    # One POS article per store
    assert len(fake_pos_manager.articles) == len(article_input.prices)
    for pos_article in fake_pos_manager.articles:
        assert pos_article.name == article_input.name
        assert pos_article.reference == uuid.UUID(result["id"]).hex

    for store_id, price in article_input.prices.items():
        pos_article = result["store_mapping"][str(store_id)]
        assert pos_article["status"] == "synced"
        assert pos_article["price"] == float(price)
        assert pos_article["raw"]["full_price"] == float(price)
