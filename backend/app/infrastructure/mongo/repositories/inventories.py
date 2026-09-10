from cleanstack import EntityId, FilterEntity, PaginatedResponse, Pagination, SortEntity
from cleanstack.mongo import AsyncMongoRepository, MongoDocument
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.domain.inventories.entities import Inventory
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

    async def get_all(
        self,
        search: str | None = None,
        filters: list[FilterEntity] | None = None,
        sort: list[SortEntity] | None = None,
        pagination: Pagination | None = None,
    ) -> PaginatedResponse[Inventory]:
        return await self.repository.get_all(
            search=search,
            filters=filters,
            sort=sort,
            pagination=pagination,
        )

    async def get_by_id(self, entity_id: EntityId, /) -> Inventory | None:
        return await self.repository.get_by_id(entity_id)

    async def save(self, entity: Inventory, /) -> None:
        await self.repository.save(entity)
