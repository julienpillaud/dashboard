import uuid
from typing import Any

from cleanstack.factories.mongo.synchronous import BaseMongoFactory
from cleanstack.mongo import MongoDocument, SyncMongoRepository
from pymongo.synchronous.client_session import ClientSession
from pymongo.synchronous.database import Database

from app.domain.articles.entities import (
    Article,
    ArticleData,
    ArticleDeposit,
    ArticleDetails,
    ArticleOrigin,
    ArticleVolume,
    PosArticle,
    RawArticle,
    VolumeUnit,
)
from app.domain.categories.entities import Category
from app.domain.stores.entities import Store
from app.domain.taxes.entities import Tax
from tests.factories.categories import CategoryFactory
from tests.factories.fake import faker
from tests.factories.stores import StoreFactory
from tests.factories.taxes import TaxFactory
from tests.factories.utils import generate_base_raw_fields


class ArticleRepository:
    domain_entity_type = Article
    collection_name = "articles"
    searchable_fields = ()

    def __init__(
        self,
        database: Database[MongoDocument],
        session: ClientSession | None = None,
    ) -> None:
        self.repository = SyncMongoRepository[Article].from_binding(
            binding=self,
            database=database,
            session=session,
        )

    def save(self, entity: Article, /) -> None:
        self.repository.save(entity)


def generate_article_volume(**kwargs: Any) -> ArticleVolume:  # noqa: ANN401
    return ArticleVolume(
        value=kwargs.get("value", faker.pyfloat(positive=True)),
        unit=kwargs.get("unit", faker.random_element(VolumeUnit)),
    )


def generate_article_deposit(**kwargs: Any) -> ArticleDeposit:  # noqa: ANN401
    return ArticleDeposit(
        unit=kwargs.get("unit", faker.pydecimal(right_digits=2, positive=True)),
        crate=kwargs.get(
            "crate",
            faker.pydecimal(right_digits=2, positive=True) if faker.boolean() else None,
        ),
        packaging=kwargs.get(
            "packaging",
            faker.random_int(min=1, max=24) if faker.boolean() else None,
        ),
    )


def generate_article_origin(**kwargs: Any) -> ArticleOrigin:  # noqa: ANN401
    return ArticleOrigin(
        name=kwargs.get("name", faker.country()),
        code=kwargs.get("code", faker.country_code() if faker.boolean() else None),
    )


def generate_article_details(**kwargs: Any) -> ArticleDetails:  # noqa: ANN401
    return ArticleDetails(
        alcohol_by_volume=kwargs.get(
            "alcohol_by_volume",
            faker.pyfloat(min_value=0, max_value=100) if faker.boolean() else None,
        ),
        volume=kwargs.get(
            "volume",
            generate_article_volume() if faker.boolean() else None,
        ),
        origin=kwargs.get(
            "origin",
            generate_article_origin() if faker.boolean() else None,
        ),
        color=kwargs.get("color", faker.color_name() if faker.boolean() else None),
        taste=kwargs.get("taste", faker.word() if faker.boolean() else None),
        distributor=kwargs.get(
            "distributor",
            faker.company() if faker.boolean() else None,
        ),
    )


def generate_article_data(**kwargs: Any) -> ArticleData:  # noqa: ANN401
    return ArticleData(
        details=kwargs.get(
            "details",
            generate_article_details() if faker.boolean() else None,
        ),
        total_cost=kwargs.get(
            "total_cost",
            faker.pydecimal(right_digits=4, positive=True),
        ),
        deposit=kwargs.get(
            "deposit",
            generate_article_deposit() if faker.boolean() else None,
        ),
    )


def generate_raw_article(**kwargs: Any) -> RawArticle:  # noqa: ANN401
    return RawArticle(
        **generate_base_raw_fields(**kwargs),
        category_id=kwargs.get("category_id", faker.hexify(text="^" * 24)),
        taxes=kwargs.get("taxes", [faker.hexify(text="^" * 24)]),
        icon_text=kwargs.get("icon_text", faker.word()),
        color=kwargs.get("color", faker.hex_color()),
        barcode=kwargs.get("barcode", faker.ean13() if faker.boolean() else None),
        in_stock=kwargs.get("in_stock", True),
        reference=kwargs.get(
            "reference", faker.bothify("REF-####") if faker.boolean() else None
        ),
        full_price=kwargs.get(
            "full_price",
            faker.pyfloat(
                positive=True,
                min_value=1,
                max_value=1000,
            )
            if faker.boolean()
            else None,
        ),
        stock_quantity=kwargs.get(
            "stock_quantity",
            faker.random_int(min=0, max=500) if faker.boolean() else None,
        ),
    )


def generate_article(
    *,
    stores: list[Store],
    tax: Tax,
    category: Category,
    **kwargs: Any,  # noqa: ANN401
) -> Article:
    return Article(
        id=uuid.uuid7(),
        name=kwargs.get("name", faker.word()),
        category=category.name,
        tax_rate=tax.rate,
        data=generate_article_data(**kwargs),
        store_mapping={
            str(store.id): PosArticle(
                store_name=store.name,
                price=kwargs.get(
                    "price", faker.pydecimal(right_digits=4, positive=True)
                ),
                raw=generate_raw_article(**kwargs),
            )
            for store in stores
        },
        created_at=kwargs.get("created_at", faker.date_time()),
        updated_at=kwargs.get("updated_at", faker.date_time()),
    )


class ArticleFactory(BaseMongoFactory[Article]):
    @property
    def store_factory(self) -> StoreFactory:
        return StoreFactory(database=self.database)

    @property
    def tax_factory(self) -> TaxFactory:
        return TaxFactory(database=self.database)

    @property
    def category_factory(self) -> CategoryFactory:
        return CategoryFactory(database=self.database)

    def build(
        self,
        *,
        stores: list[Store] | None = None,
        tax: Tax | None = None,
        category: Category | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Article:
        stores = stores or self.store_factory.create_many(3)
        tax = tax or self.tax_factory.create_one(stores=stores)
        category = category or self.category_factory.create_one(stores=stores)
        return generate_article(
            stores=stores,
            tax=tax,
            category=category,
            **kwargs,
        )

    @property
    def _repository(self) -> ArticleRepository:
        return ArticleRepository(database=self.database)
