from typing import Protocol

from cleanstack import EntityId, FilterEntity, PaginatedResponse, Pagination, SortEntity

from app.domain.inventories.entities import Inventory


class InventoryRepositoryProtocol(Protocol):
    async def get_all(
        self,
        search: str | None = None,
        filters: list[FilterEntity] | None = None,
        sort: list[SortEntity] | None = None,
        pagination: Pagination | None = None,
    ) -> PaginatedResponse[Inventory]: ...

    async def get_by_id(self, entity_id: EntityId, /) -> Inventory | None: ...

    async def save(self, entity: Inventory, /) -> None: ...
