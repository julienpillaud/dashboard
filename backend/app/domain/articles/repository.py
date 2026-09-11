from typing import Protocol

from cleanstack import FilterEntity, PaginatedResponse, Pagination, SortEntity

from app.domain.articles.entities import Article


class ArticleRepositoryProtocol(Protocol):
    async def get_all(
        self,
        search: str | None = None,
        filters: list[FilterEntity] | None = None,
        sort: list[SortEntity] | None = None,
        pagination: Pagination | None = None,
    ) -> PaginatedResponse[Article]: ...

    async def count(self, filters: list[FilterEntity] | None = None) -> int: ...

    async def save_many(self, entities: list[Article], /) -> None: ...

    async def delete_many(self, entities: list[Article], /) -> None: ...
