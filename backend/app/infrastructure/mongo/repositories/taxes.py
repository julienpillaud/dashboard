from cleanstack import Pagination, SortEntity
from cleanstack.mongo import AsyncMongoRepository, MongoDocument
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.domain.taxes.entities import Tax
from app.domain.taxes.repository import TaxRepositoryProtocol


class TaxRepository(TaxRepositoryProtocol):
    domain_entity_type = Tax
    collection_name = "taxes"
    searchable_fields = ()

    def __init__(
        self,
        database: AsyncDatabase[MongoDocument],
        session: AsyncClientSession | None = None,
    ) -> None:
        self.repository = AsyncMongoRepository[Tax].from_binding(
            binding=self,
            database=database,
            session=session,
        )

    async def get_all(self, sort: list[SortEntity] | None = None) -> list[Tax]:
        total = await self.repository.collection.count_documents({})

        if total == 0:
            return []

        result = await self.repository.get_all(
            sort=sort,
            pagination=Pagination(size=total),
        )
        return result.items

    async def get_by_rate(self, rate: float) -> Tax | None:
        result = await self.repository.collection.find_one({"rate": rate})
        return self.repository.to_domain_entity(result) if result else None

    async def save_many(self, entities: list[Tax], /) -> None:
        if not entities:
            return

        db_entities = [
            self.repository.to_database_entity(entity) for entity in entities
        ]
        await self.repository.collection.insert_many(
            documents=db_entities,
            session=self.repository.session,
        )
