from fastapi import status
from fastapi.testclient import TestClient

from app.domain.articles.entities import ArticleCreate
from tests.factories.factory import Factory


def test_create_article(factory: Factory, tokens: None, client: TestClient) -> None:
    data = factory.articles.build()
    article_create = ArticleCreate(
        name=data.name,
        category=data.category,
        total_cost=data.total_cost,
        tax_rate=data.tax_rate,
        distributor=data.distributor,
        details=data.details,
        price=1.7,
    )

    response = client.post("/api/articles", json=article_create.model_dump())

    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert result["name"] == article_create.name
    assert result["category"] == article_create.category
    assert result["total_cost"] == float(article_create.total_cost)
    assert result["tax_rate"] == article_create.tax_rate
    assert result["distributor"] == article_create.distributor
