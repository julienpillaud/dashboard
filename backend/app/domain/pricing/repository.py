from typing import Protocol

from cleanstack import EntityId

from app.domain.pricing.entities import PricingRule


class PricingRuleRepositoryProtocol(Protocol):
    async def get_by_store_and_category(
        self,
        store_id: EntityId,
        category_id: EntityId,
    ) -> PricingRule | None: ...

    async def save_many(self, entities: list[PricingRule], /) -> None: ...
