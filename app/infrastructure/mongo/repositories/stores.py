from cleanstack.mongo import AsyncMongoRepository

from app.domain.stores.entities import Store
from app.domain.stores.repository import StoreRepositoryProtocol


class StoreRepository(AsyncMongoRepository[Store], StoreRepositoryProtocol):
    domain_entity_type = Store
    collection_name = "stores"

    async def get_by_slug(self, slug: str) -> Store | None:
        result = await self.collection.find_one({"slug": slug})
        return self.to_domain_entity(result) if result else None
