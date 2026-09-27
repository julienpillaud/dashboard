from cleanstack import Pagination, SortEntity
from cleanstack.mongo import AsyncMongoRepository, MongoDocument
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.domain.categories.entities import Category
from app.domain.categories.repository import CategoryRepositoryProtocol


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

    async def get_all(self, sort: list[SortEntity] | None = None) -> list[Category]:
        total = await self.repository.collection.count_documents({})

        if total == 0:
            return []

        result = await self.repository.get_all(
            sort=sort,
            pagination=Pagination(size=total),
        )
        return result.items

    async def get_by_name(self, name: str) -> Category | None:
        result = await self.repository.collection.find_one({"name": name})
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
