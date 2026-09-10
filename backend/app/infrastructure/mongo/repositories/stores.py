from cleanstack import FilterEntity, PaginatedResponse, Pagination, SortEntity
from cleanstack.mongo import AsyncMongoRepository, MongoDocument
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.domain.stores.entities import Store
from app.domain.stores.repository import StoreRepositoryProtocol


class StoreRepository(StoreRepositoryProtocol):
    domain_entity_type = Store
    collection_name = "stores"
    searchable_fields = ()

    def __init__(
        self,
        database: AsyncDatabase[MongoDocument],
        session: AsyncClientSession | None = None,
    ) -> None:
        self.repository = AsyncMongoRepository[Store].from_binding(
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
    ) -> PaginatedResponse[Store]:
        return await self.repository.get_all(
            search=search,
            filters=filters,
            sort=sort,
            pagination=pagination,
        )

    async def get_by_slug(self, slug: str) -> Store | None:
        result = await self.repository.collection.find_one({"slug": slug})
        return self.repository.to_domain_entity(result) if result else None

    async def save_many(self, entities: list[Store], /) -> None:
        if not entities:
            return

        db_entities = [
            self.repository.to_database_entity(entity) for entity in entities
        ]
        await self.repository.collection.insert_many(
            documents=db_entities,
            session=self.repository.session,
        )
