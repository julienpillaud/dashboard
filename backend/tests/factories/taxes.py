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


def generate_tax(*, store: Store, **kwargs: Any) -> Tax:  # noqa: ANN401
    return Tax(
        id=uuid.uuid7(),
        store_id=store.id,
        store_name=store.name,
        raw=RawTax(
            **generate_base_raw_fields(**kwargs),
            rate=kwargs.get("rate", faker.pyfloat()),
        ),
    )


class TaxFactory(BaseMongoFactory[Tax]):
    @property
    def store_factory(self) -> StoreFactory:
        return StoreFactory(database=self.database)

    def build(
        self,
        *,
        store: Store | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Tax:
        store = store or self.store_factory.create_one()
        return generate_tax(store=store, **kwargs)

    @property
    def _repository(self) -> TaxRepository:
        return TaxRepository(database=self.database)
