import uuid
from typing import Any

from cleanstack.factories.mongo.synchronous import BaseMongoFactory
from cleanstack.mongo import MongoDocument, SyncMongoRepository
from pymongo.synchronous.client_session import ClientSession
from pymongo.synchronous.database import Database

from app.domain.stores.entities import Store
from tests.factories.fake import faker


class StoreRepository:
    domain_entity_type = Store
    collection_name = "stores"
    searchable_fields = ()

    def __init__(
        self,
        database: Database[MongoDocument],
        session: ClientSession | None = None,
    ) -> None:
        self.repository = SyncMongoRepository[Store].from_binding(
            binding=self,
            database=database,
            session=session,
        )

    def save(self, entity: Store, /) -> None:
        self.repository.save(entity)


def generate_store(**kwargs: Any) -> Store:  # noqa: ANN401
    name = kwargs.get("name", faker.name())
    slug = name.lower()
    return Store(
        id=uuid.uuid7(),
        name=name,
        slug=slug,
        pos_api_key=faker.hexify(text="^" * 24),
    )


class StoreFactory(BaseMongoFactory[Store]):
    def build(self, **kwargs: Any) -> Store:  # noqa: ANN401
        return generate_store(**kwargs)

    @property
    def _repository(self) -> StoreRepository:
        return StoreRepository(database=self.database)
