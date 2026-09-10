from typing import Protocol

from cleanstack import FilterEntity, PaginatedResponse, Pagination, SortEntity

from app.domain.categories.entities import Category
from app.domain.stores.entities import Store


class CategoryRepositoryProtocol(Protocol):
    async def get_all(
        self,
        search: str | None = None,
        filters: list[FilterEntity] | None = None,
        sort: list[SortEntity] | None = None,
        pagination: Pagination | None = None,
    ) -> PaginatedResponse[Category]: ...

    async def get_by_external_id(
        self,
        current_store: Store,
        external_id: str,
    ) -> Category | None: ...

    async def save_many(self, entities: list[Category], /) -> None: ...

    async def update_many(self, entities: list[Category], /) -> None: ...

    async def delete_many(self, entities: list[Category], /) -> None: ...
