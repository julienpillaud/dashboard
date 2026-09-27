from typing import Protocol

from cleanstack import SortEntity

from app.domain.categories.entities import Category


class CategoryRepositoryProtocol(Protocol):
    async def get_all(self, sort: list[SortEntity] | None = None) -> list[Category]: ...

    async def get_by_name(self, name: str) -> Category | None: ...

    async def save_many(self, entities: list[Category], /) -> None: ...
