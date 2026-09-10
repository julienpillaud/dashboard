from typing import Protocol

from cleanstack import FilterEntity, PaginatedResponse, Pagination, SortEntity

from app.domain.stores.entities import Store
from app.domain.taxes.entities import Tax


class TaxRepositoryProtocol(Protocol):
    async def get_all(
        self,
        search: str | None = None,
        filters: list[FilterEntity] | None = None,
        sort: list[SortEntity] | None = None,
        pagination: Pagination | None = None,
    ) -> PaginatedResponse[Tax]: ...

    async def get_by_external_id(
        self,
        current_store: Store,
        external_id: str,
    ) -> Tax | None: ...

    async def save_many(self, entities: list[Tax], /) -> None: ...

    async def update_many(self, entities: list[Tax], /) -> None: ...

    async def delete_many(self, entities: list[Tax], /) -> None: ...
