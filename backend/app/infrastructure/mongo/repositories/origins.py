from cleanstack.mongo import AsyncMongoRepository, MongoDocument
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.domain.origins.entities import Origin
from app.domain.origins.repository import OriginRepositoryProtocol


class OriginRepository(OriginRepositoryProtocol):
    domain_entity_type = Origin
    collection_name = "origins"
    searchable_fields = ()

    def __init__(
        self,
        database: AsyncDatabase[MongoDocument],
        session: AsyncClientSession | None = None,
    ) -> None:
        self.repository = AsyncMongoRepository[Origin].from_binding(
            binding=self,
            database=database,
            session=session,
        )

    async def get_all(self) -> list[Origin]:
        cursor = self.repository.collection.find()
        items = await cursor.to_list()
        return [self.repository.to_domain_entity(item) for item in items]

    async def save_many(self, entities: list[Origin], /) -> None:
        if not entities:
            return

        db_entities = [
            self.repository.to_database_entity(entity) for entity in entities
        ]
        await self.repository.collection.insert_many(
            documents=db_entities,
            session=self.repository.session,
        )
