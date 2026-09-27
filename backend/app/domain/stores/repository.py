from typing import Protocol

from app.domain.stores.entities import Store


class StoreRepositoryProtocol(Protocol):
    async def get_all(self) -> list[Store]: ...

    async def get_by_slug(self, slug: str) -> Store | None: ...

    async def save_many(self, entities: list[Store], /) -> None: ...
