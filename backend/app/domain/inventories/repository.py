from typing import Protocol

from cleanstack import EntityId

from app.domain.inventories.entities import Inventory, InventorySummary


class InventoryRepositoryProtocol(Protocol):
    async def get_summaries_by_store(
        self,
        entity_id: EntityId,
        /,
    ) -> list[InventorySummary]: ...

    async def get_by_id(self, entity_id: EntityId, /) -> Inventory | None: ...

    async def save(self, entity: Inventory, /) -> None: ...
