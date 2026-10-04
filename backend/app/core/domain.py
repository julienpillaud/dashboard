import time
from collections.abc import Awaitable, Callable
from types import TracebackType
from typing import Concatenate

from app.core.logger import logger
from app.core.protocols import ContextProviderProtocol, UnitOfWorkProtocol
from app.domain.context import ContextProtocol


class Domain:
    def __init__(self, context: ContextProtocol) -> None:
        self._context = context

    async def run[**P, R](
        self,
        func: Callable[Concatenate[ContextProtocol, P], Awaitable[R]],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        return await func(self._context, *args, **kwargs)


class DomainScope:
    def __init__(
        self,
        uow: UnitOfWorkProtocol,
        context_provider: ContextProviderProtocol,
        transactional: bool,
    ) -> None:
        self.uow = uow
        self.context_provider = context_provider
        self.transactional = transactional

    async def __aenter__(self) -> Domain:
        logger.debug("Start Use case")
        self._start_time = time.perf_counter()

        await self.uow.start(transactional=self.transactional)
        return Domain(context=self.context_provider(self.uow))

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.uow.end(error=exc_val)

        elapsed = (time.perf_counter() - self._start_time) * 1000
        logger.info(f"Use case [{elapsed:.1f} ms]")
