from typing import Protocol

from cleanstack import EntityId

from app.domain.refresh_tokens.entities import RefreshToken


class RefreshTokenRepositoryProtocol(Protocol):
    async def save(self, entity: RefreshToken, /) -> None: ...

    async def get_by_hash(self, value: str, /) -> RefreshToken | None: ...

    async def revoke(self, token_id: EntityId) -> None: ...

    async def revoke_for_user(self, user_id: EntityId) -> None: ...
