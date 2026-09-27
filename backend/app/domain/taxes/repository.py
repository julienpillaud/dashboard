from typing import Protocol

from cleanstack import SortEntity

from app.domain.taxes.entities import Tax


class TaxRepositoryProtocol(Protocol):
    async def get_all(self, sort: list[SortEntity] | None = None) -> list[Tax]: ...

    async def get_by_rate(self, rate: float) -> Tax | None: ...

    async def save_many(self, entities: list[Tax], /) -> None: ...
