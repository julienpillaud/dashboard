from typing import Protocol

from app.domain.context import ContextProtocol


class UnitOfWorkProtocol(Protocol):
    async def start(self, transactional: bool) -> None: ...

    async def end(self, error: BaseException | None) -> None: ...


class ContextProviderProtocol(Protocol):
    def __call__(self, uow: UnitOfWorkProtocol) -> ContextProtocol: ...
