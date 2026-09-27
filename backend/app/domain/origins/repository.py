from typing import Protocol

from app.domain.origins.entities import Origin


class OriginRepositoryProtocol(Protocol):
    async def get_all(self) -> list[Origin]: ...

    async def save_many(self, entities: list[Origin], /) -> None: ...
