import uuid
from typing import Any

from cleanstack.factories.mongo.synchronous import BaseMongoFactory
from cleanstack.mongo import MongoDocument, SyncMongoRepository
from pymongo.synchronous.client_session import ClientSession
from pymongo.synchronous.database import Database

from app.domain.stores.entities import Store
from app.domain.taxes.entities import RawTax, Tax
from tests.factories.fake import faker
from tests.factories.stores import StoreFactory
from tests.factories.utils import generate_base_raw_fields


class TaxRepository:
    domain_entity_type = Tax
    collection_name = "taxes"
    searchable_fields = ()

    def __init__(
        self,
        database: Database[MongoDocument],
        session: ClientSession | None = None,
    ) -> None:
        self.repository = SyncMongoRepository[Tax].from_binding(
            binding=self,
            database=database,
            session=session,
        )

    def save(self, entity: Tax, /) -> None:
        self.repository.save(entity)


def generate_raw_tax(**kwargs: Any) -> RawTax:  # noqa: ANN401
    return RawTax(
        **generate_base_raw_fields(**kwargs),
        rate=kwargs.get("rate", faker.pyfloat()),
    )


def generate_tax(*, stores: list[Store], **kwargs: Any) -> Tax:  # noqa: ANN401
    return Tax(
        id=uuid.uuid7(),
        rate=kwargs.get("rate", faker.pyfloat()),
        store_mapping={str(store.id): generate_raw_tax(**kwargs) for store in stores},
    )


class TaxFactory(BaseMongoFactory[Tax]):
    @property
    def store_factory(self) -> StoreFactory:
        return StoreFactory(database=self.database)

    def build(
        self,
        *,
        stores: list[Store] | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Tax:
        stores = stores or self.store_factory.create_many(3)
        return generate_tax(stores=stores, **kwargs)

    @property
    def _repository(self) -> TaxRepository:
        return TaxRepository(database=self.database)
