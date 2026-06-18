from cleanstack.mongo import AsyncMongoRepository

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
