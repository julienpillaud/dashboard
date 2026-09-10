from cleanstack import FilterEntity, PaginatedResponse, Pagination, SortEntity
from cleanstack.mongo import AsyncMongoRepository, MongoDocument
from pymongo import DeleteOne, UpdateOne
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.domain.categories.entities import Category
from app.domain.categories.repository import CategoryRepositoryProtocol
from app.domain.stores.entities import Store


class CategoryRepository(CategoryRepositoryProtocol):
    domain_entity_type = Category
    collection_name = "categories"
    searchable_fields = ()

    def __init__(
        self,
        database: AsyncDatabase[MongoDocument],
        session: AsyncClientSession | None = None,
    ) -> None:
        self.repository = AsyncMongoRepository[Category].from_binding(
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
    ) -> PaginatedResponse[Category]:
        return await self.repository.get_all(
            search=search,
            filters=filters,
            sort=sort,
            pagination=pagination,
        )

    async def get_by_external_id(
        self,
        current_store: Store,
        external_id: str,
    ) -> Category | None:
        result = await self.repository.collection.find_one(
            {"store_id": current_store.id, "external_id": external_id}
        )
        return self.repository.to_domain_entity(result) if result else None

    async def save_many(self, entities: list[Category], /) -> None:
        if not entities:
            return

        db_entities = [
            self.repository.to_database_entity(entity) for entity in entities
        ]
        await self.repository.collection.insert_many(
            documents=db_entities,
            session=self.repository.session,
        )

    async def update_many(self, entities: list[Category], /) -> None:
        if not entities:
            return

        requests = [
            UpdateOne(
                {"_id": entity.id},
                {"$set": entity.model_dump(exclude={"id"})},
            )
            for entity in entities
        ]
        await self.repository.collection.bulk_write(requests=requests, ordered=False)

    async def delete_many(self, entities: list[Category], /) -> None:
        if not entities:
            return

        requests = [DeleteOne({"_id": entity.id}) for entity in entities]
        await self.repository.collection.bulk_write(requests=requests, ordered=False)
