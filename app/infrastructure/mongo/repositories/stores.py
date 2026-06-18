from cleanstack.mongo import AsyncMongoRepository

from app.domain.stores.entities import Store
from app.domain.stores.repository import StoreRepositoryProtocol


class StoreRepository(AsyncMongoRepository[Store], StoreRepositoryProtocol):
    domain_entity_type = Store
    collection_name = "stores"

    async def get_by_name(self, name: str) -> Store | None:
        result = await self.collection.find_one({"name": name})
        return self.to_domain_entity(result) if result else None
