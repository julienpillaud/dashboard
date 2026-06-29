from typing import Protocol

from cleanstack import (
    BaseEntity,
    EntityId,
    FilterEntity,
    PaginatedResponse,
    Pagination,
    SortEntity,
)

from app.domain.articles.entities import RawArticle
from app.domain.categories.entities import RawCategory
from app.domain.taxes.entities import RawTax


class RepositoryProtocol[T: BaseEntity](Protocol):
    async def get_all(
        self,
        search: str | None = None,
        filters: list[FilterEntity] | None = None,
        sort: list[SortEntity] | None = None,
        pagination: Pagination | None = None,
    ) -> PaginatedResponse[T]: ...

    async def get_by_id(self, entity_id: EntityId, /) -> T | None: ...

    async def save(self, entity: T, /) -> None: ...

    async def update(self, entity: T, /) -> None: ...

    async def remove(self, entity: T, /) -> None: ...


class POSManagerProtocol(Protocol):
    async def get_taxes(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawTax]: ...

    async def get_categories(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawCategory]: ...

    async def get_articles(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawArticle]: ...
