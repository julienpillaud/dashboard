import uuid
from typing import Any

from cleanstack.factories.mongo.synchronous import BaseMongoFactory
from cleanstack.mongo import MongoDocument, SyncMongoRepository
from pymongo.synchronous.client_session import ClientSession
from pymongo.synchronous.database import Database

from app.domain.categories.entities import Category, CategoryFields, RawCategory
from app.domain.stores.entities import Store
from tests.factories.fake import faker
from tests.factories.stores import StoreFactory
from tests.factories.utils import generate_base_raw_fields


class CategoryRepository:
    domain_entity_type = Category
    collection_name = "categories"
    searchable_fields = ()

    def __init__(
        self,
        database: Database[MongoDocument],
        session: ClientSession | None = None,
    ) -> None:
        self.repository = SyncMongoRepository[Category].from_binding(
            binding=self,
            database=database,
            session=session,
        )

    def save(self, entity: Category, /) -> None:
        self.repository.save(entity)


def generate_raw_category(**kwargs: Any) -> RawCategory:  # noqa: ANN401
    return RawCategory(
        **generate_base_raw_fields(**kwargs),
        icon_text=kwargs.get("icon_text", faker.word()),
        color=kwargs.get("color", faker.color()),
    )


def generate_category_fields(**kwargs: Any) -> CategoryFields:  # noqa: ANN401
    return CategoryFields(
        origin=kwargs.get("origin", faker.boolean()),
        color=kwargs.get("color", faker.boolean()),
        taste=kwargs.get("taste", faker.boolean()),
        volume=kwargs.get("volume", faker.boolean()),
        alcohol_by_volume=kwargs.get("alcohol_by_volume", faker.boolean()),
        deposit_unit=kwargs.get("deposit_unit", faker.boolean()),
        deposit_crate=kwargs.get("deposit_crate", faker.boolean()),
        deposit_packaging=kwargs.get("deposit_packaging", faker.boolean()),
    )


def generate_category(*, stores: list[Store], **kwargs: Any) -> Category:  # noqa: ANN401
    return Category(
        id=uuid.uuid7(),
        name=kwargs.get("name", faker.word()),
        fields=generate_category_fields(**kwargs),
        store_mapping={
            str(store.id): generate_raw_category(**kwargs) for store in stores
        },
    )


class CategoryFactory(BaseMongoFactory[Category]):
    @property
    def store_factory(self) -> StoreFactory:
        return StoreFactory(database=self.database)

    def build(
        self,
        *,
        stores: list[Store] | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Category:
        stores = stores or self.store_factory.create_many(3)
        return generate_category(stores=stores, **kwargs)

    @property
    def _repository(self) -> CategoryRepository:
        return CategoryRepository(database=self.database)
