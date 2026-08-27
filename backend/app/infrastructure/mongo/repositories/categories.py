from cleanstack.mongo import AsyncMongoRepository
from pymongo import UpdateOne

from app.domain.categories.entities import Category
from app.domain.categories.repository import CategoryRepositoryProtocol
from app.domain.stores.entities import Store


class CategoryRepository(AsyncMongoRepository[Category], CategoryRepositoryProtocol):
    domain_entity_type = Category
    collection_name = "categories"

    async def get_by_external_id(
        self,
        current_store: Store,
        external_id: str,
    ) -> Category | None:
        result = await self.collection.find_one(
            {"store_id": current_store.id, "external_id": external_id}
        )
        return self.to_domain_entity(result) if result else None

    async def save_many(self, entities: list[Category], /) -> None:
        if not entities:
            return

        db_entities = [self.to_database_entity(entity) for entity in entities]
        await self.collection.insert_many(
            documents=db_entities,
            session=self.session,
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
        await self.collection.bulk_write(requests=requests, ordered=False)
