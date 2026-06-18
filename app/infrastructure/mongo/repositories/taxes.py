from cleanstack.mongo import AsyncMongoRepository

from app.domain.stores.entities import Store
from app.domain.taxes.entities import Tax
from app.domain.taxes.repository import TaxRepositoryProtocol


class TaxRepository(AsyncMongoRepository[Tax], TaxRepositoryProtocol):
    domain_entity_type = Tax
    collection_name = "taxes"

    async def get_by_external_id(
        self,
        current_store: Store,
        external_id: str,
    ) -> Tax | None:
        result = await self.collection.find_one(
            {
                "store_id": current_store.id,
                "external_id": external_id,
            }
        )
        return self.to_domain_entity(result) if result else None
