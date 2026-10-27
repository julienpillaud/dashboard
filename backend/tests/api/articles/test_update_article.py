import uuid
from decimal import Decimal

from cleanstack.mongo import MongoDocument
from fastapi import status
from fastapi.testclient import TestClient
from pymongo.synchronous.database import Database

from app.domain.articles.entities import Article, ArticleInput, POSStatus
from tests.factories.factory import Factory
from tests.mocks.pos_manager import FakePOSManager


def build_article_input(
    article: Article,
    name: str | None = None,
    prices: dict[uuid.UUID, Decimal] | None = None,
) -> ArticleInput:
    # By default: same name, a new price for every store
    return ArticleInput(
        name=name or article.name,
        category=article.category,
        total_cost=article.total_cost,
        tax_rate=article.tax_rate,
        distributor=article.distributor,
        details=article.details,
        prices=prices
        or {
            uuid.UUID(store_id): Decimal(f"{10 + index}.50")
            for index, store_id in enumerate(article.store_mapping)
        },
    )


def current_prices(article: Article) -> dict[uuid.UUID, Decimal]:
    return {
        uuid.UUID(store_id): pos_article.price
        for store_id, pos_article in article.store_mapping.items()
    }


def test_update_article(
    factory: Factory,
    tokens: None,
    client: TestClient,
    fake_pos_manager: FakePOSManager,
    database: Database[MongoDocument],
) -> None:
    article = factory.articles.create_one()
    fake_pos_manager.add_articles(
        [p.raw for p in article.store_mapping.values() if p.raw]
    )
    article_input = build_article_input(article, name="Updated name")

    response = client.put(
        f"/api/articles/{article.id}",
        json=article_input.model_dump(mode="json"),
    )

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["name"] == article_input.name

    pos_articles = {a.id: a for a in fake_pos_manager.articles}
    for store_id, price in article_input.prices.items():
        raw = article.store_mapping[str(store_id)].raw
        assert raw is not None
        pos_article = pos_articles[raw.id]
        assert pos_article.name == article_input.name
        assert pos_article.full_price == price
        assert pos_article.reference == article.id.hex

        mapping = result["store_mapping"][str(store_id)]
        assert mapping["price"] == float(price)
        assert mapping["status"] == "synced"

    # The article is persisted, not only returned
    document = database["articles"].find_one({"_id": article.id})
    assert document is not None
    assert document["name"] == article_input.name
    for store_id, price in article_input.prices.items():
        assert document["store_mapping"][str(store_id)]["price"] == float(price)
        assert document["store_mapping"][str(store_id)]["status"] == "synced"


def test_update_article_partial_failure(
    factory: Factory,
    tokens: None,
    client: TestClient,
    fake_pos_manager: FakePOSManager,
) -> None:
    # Only the first store has the article in the POS: the others fail
    article = factory.articles.create_one()
    store_ids = list(article.store_mapping)
    first_raw = article.store_mapping[store_ids[0]].raw
    assert first_raw is not None
    fake_pos_manager.add_articles([first_raw])
    article_input = build_article_input(article, name="Updated name")

    response = client.put(
        f"/api/articles/{article.id}",
        json=article_input.model_dump(mode="json"),
    )

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["name"] == article_input.name

    succeeded = result["store_mapping"][store_ids[0]]
    assert succeeded["price"] == float(article_input.prices[uuid.UUID(store_ids[0])])
    assert succeeded["status"] == "synced"

    for store_id in store_ids[1:]:
        failed = result["store_mapping"][store_id]
        assert failed["price"] == float(article.store_mapping[store_id].price)
        assert failed["status"] == "out_of_sync"


def test_update_article_not_created_in_store(
    factory: Factory,
    tokens: None,
    client: TestClient,
    fake_pos_manager: FakePOSManager,
    database: Database[MongoDocument],
) -> None:
    # The creation failed in one store: the article has no POS article there
    article = factory.articles.create_one()
    missing_store_id = next(iter(article.store_mapping))
    database["articles"].update_one(
        {"_id": article.id},
        {
            "$set": {
                f"store_mapping.{missing_store_id}.raw": None,
                f"store_mapping.{missing_store_id}.status": POSStatus.NOT_CREATED,
            }
        },
    )
    pos_articles = [
        p.raw
        for store_id, p in article.store_mapping.items()
        if p.raw and store_id != missing_store_id
    ]
    fake_pos_manager.add_articles(pos_articles)
    article_input = build_article_input(article, name="Updated name")

    response = client.put(
        f"/api/articles/{article.id}",
        json=article_input.model_dump(mode="json"),
    )

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["name"] == article_input.name

    # The store without POS article is skipped and keeps its state
    skipped = result["store_mapping"][missing_store_id]
    assert skipped["status"] == POSStatus.NOT_CREATED
    assert skipped["raw"] is None
    assert skipped["price"] == float(article.store_mapping[missing_store_id].price)

    # The other stores are updated
    assert sorted(fake_pos_manager.update_calls) == sorted(p.id for p in pos_articles)
    for store_id in article.store_mapping:
        if store_id == missing_store_id:
            continue
        mapping = result["store_mapping"][store_id]
        assert mapping["status"] == POSStatus.SYNCED
        assert mapping["price"] == float(article_input.prices[uuid.UUID(store_id)])


def test_update_article_without_pos_changes(
    factory: Factory,
    tokens: None,
    client: TestClient,
    fake_pos_manager: FakePOSManager,
    database: Database[MongoDocument],
) -> None:
    # Only a field that lives in our database changes: the POS is not called
    article = factory.articles.create_one(price=Decimal("9.90"))
    fake_pos_manager.add_articles(
        [p.raw for p in article.store_mapping.values() if p.raw]
    )
    article_input = build_article_input(article, prices=current_prices(article))
    article_input.distributor = "New distributor"

    response = client.put(
        f"/api/articles/{article.id}",
        json=article_input.model_dump(mode="json"),
    )

    assert response.status_code == status.HTTP_200_OK
    assert fake_pos_manager.update_calls == []

    document = database["articles"].find_one({"_id": article.id})
    assert document is not None
    assert document["distributor"] == "New distributor"


def test_update_article_price_changed_in_one_store(
    factory: Factory,
    tokens: None,
    client: TestClient,
    fake_pos_manager: FakePOSManager,
) -> None:
    # Only one store price changes: only this store is called
    article = factory.articles.create_one(price=Decimal("9.90"))
    fake_pos_manager.add_articles(
        [p.raw for p in article.store_mapping.values() if p.raw]
    )
    changed_store_id = next(iter(article.store_mapping))
    prices = current_prices(article)
    price_to_test = 12.5
    prices[uuid.UUID(changed_store_id)] = Decimal(price_to_test)
    article_input = build_article_input(article, prices=prices)

    response = client.put(
        f"/api/articles/{article.id}",
        json=article_input.model_dump(mode="json"),
    )

    assert response.status_code == status.HTTP_200_OK
    changed_raw = article.store_mapping[changed_store_id].raw
    assert changed_raw is not None
    assert fake_pos_manager.update_calls == [changed_raw.id]

    mapping = response.json()["store_mapping"][changed_store_id]
    assert mapping["status"] == POSStatus.SYNCED
    assert mapping["price"] == price_to_test


def test_update_article_out_of_sync_is_retried(
    factory: Factory,
    tokens: None,
    client: TestClient,
    fake_pos_manager: FakePOSManager,
) -> None:
    # The last update failed: the stores are called again even without changes
    article = factory.articles.create_one(
        price=Decimal("9.90"),
        status=POSStatus.OUT_OF_SYNC,
    )
    pos_articles = [p.raw for p in article.store_mapping.values() if p.raw]
    fake_pos_manager.add_articles(pos_articles)
    article_input = build_article_input(article, prices=current_prices(article))

    response = client.put(
        f"/api/articles/{article.id}",
        json=article_input.model_dump(mode="json"),
    )

    assert response.status_code == status.HTTP_200_OK
    assert sorted(fake_pos_manager.update_calls) == sorted(p.id for p in pos_articles)
    for mapping in response.json()["store_mapping"].values():
        assert mapping["status"] == POSStatus.SYNCED


def test_update_article_pos_failure(
    factory: Factory,
    tokens: None,
    client: TestClient,
) -> None:
    # The fake POS is empty: every update fails with an unknown article
    article = factory.articles.create_one()
    article_input = build_article_input(article, name="Updated name")

    response = client.put(
        f"/api/articles/{article.id}",
        json=article_input.model_dump(mode="json"),
    )

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["name"] == article_input.name
    for store_id, pos_article in article.store_mapping.items():
        mapping = result["store_mapping"][store_id]
        assert mapping["price"] == float(pos_article.price)
        assert mapping["status"] == "out_of_sync"


def test_update_article_not_found(
    factory: Factory,
    tokens: None,
    client: TestClient,
) -> None:
    article = factory.articles.build()
    article_input = build_article_input(article, name="Updated name")

    response = client.put(
        f"/api/articles/{article.id}",
        json=article_input.model_dump(mode="json"),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
