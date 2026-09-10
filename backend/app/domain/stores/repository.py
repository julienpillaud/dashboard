from typing import Protocol

from cleanstack import FilterEntity, PaginatedResponse, Pagination, SortEntity

from app.domain.stores.entities import Store


class StoreRepositoryProtocol(Protocol):
    async def get_all(
        self,
        search: str | None = None,
        filters: list[FilterEntity] | None = None,
        sort: list[SortEntity] | None = None,
        pagination: Pagination | None = None,
    ) -> PaginatedResponse[Store]: ...

    async def get_by_slug(self, slug: str) -> Store | None: ...

    async def save_many(self, entities: list[Store], /) -> None: ...
