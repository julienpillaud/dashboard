from cleanstack import EntityId
from cleanstack.mongo import AsyncMongoRepository, MongoDocument
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.domain.pricing.entities import PricingRule
from app.domain.pricing.repository import PricingRuleRepositoryProtocol


class PricingRuleRepository(PricingRuleRepositoryProtocol):
    domain_entity_type = PricingRule
    collection_name = "pricing_rules"
    searchable_fields = ()

    def __init__(
        self,
        database: AsyncDatabase[MongoDocument],
        session: AsyncClientSession | None = None,
    ) -> None:
        self.repository = AsyncMongoRepository[PricingRule].from_binding(
            binding=self,
            database=database,
            session=session,
        )

    async def get_by_store_and_category(
        self,
        store_id: EntityId,
        category_id: EntityId,
    ) -> PricingRule | None:
        result = await self.repository.collection.find_one(
            {
                "store_id": store_id,
                "category_id": category_id,
            },
            session=self.repository.session,
        )
        return self.repository.to_domain_entity(result) if result else None

    async def save_many(self, entities: list[PricingRule], /) -> None:
        if not entities:
            return

        db_entities = [
            self.repository.to_database_entity(entity) for entity in entities
        ]
        await self.repository.collection.insert_many(
            documents=db_entities,
            session=self.repository.session,
        )
