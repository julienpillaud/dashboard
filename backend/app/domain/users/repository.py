from typing import Protocol

from cleanstack import EntityId

from app.domain.users.entities import User


class UserRepositoryProtocol(Protocol):
    async def get_by_id(self, entity_id: EntityId, /) -> User | None: ...

    async def get_by_name(self, name: str) -> User | None: ...
