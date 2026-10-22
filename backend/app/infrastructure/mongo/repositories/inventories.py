from cleanstack import EntityId
from cleanstack.mongo import AsyncMongoRepository, MongoDocument
from cleanstack.mongo.utils import normalize_ids
from pymongo import DESCENDING
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.domain.inventories.entities import Inventory, InventorySummary
from app.domain.inventories.repository import InventoryRepositoryProtocol


class InventoryRepository(InventoryRepositoryProtocol):
    domain_entity_type = Inventory
    collection_name = "inventories"
    searchable_fields = ()

    def __init__(
        self,
        database: AsyncDatabase[MongoDocument],
        session: AsyncClientSession | None = None,
    ) -> None:
        self.repository = AsyncMongoRepository[Inventory].from_binding(
            binding=self,
            database=database,
            session=session,
        )

    async def get_summaries_by_store(
        self,
        entity_id: EntityId,
        /,
    ) -> list[InventorySummary]:
        cursor = self.repository.collection.find(
            filter={"store_id": entity_id},
            projection={"records": False},
            sort=[("created_at", DESCENDING)],
            session=self.repository.session,
        )
        documents = await cursor.to_list()
        for document in documents:
            normalize_ids(document)
        return [InventorySummary.model_validate(document) for document in documents]

    async def get_by_id(self, entity_id: EntityId, /) -> Inventory | None:
        return await self.repository.get_by_id(entity_id)

    async def save(self, entity: Inventory, /) -> None:
        await self.repository.save(entity)
