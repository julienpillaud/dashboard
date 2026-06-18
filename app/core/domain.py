import logging
import time
from collections.abc import Awaitable, Callable
from types import TracebackType
from typing import Concatenate

from app.core.context import ContextFactory
from app.domain.context import ContextProtocol
from app.infrastructure.mongo.resource import AsyncMongoResource

logger = logging.getLogger("app")


class Domain:
    def __init__(
        self,
        resource: AsyncMongoResource,
        context_factory: ContextFactory,
    ) -> None:
        self.resource = resource
        self.context_factory = context_factory
        self.command_name = ""

    async def run[**P, R](
        self,
        command: Callable[Concatenate[ContextProtocol, P], Awaitable[R]],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        self.command_name = getattr(command, "__name__", "unknown")
        return await command(self.context, *args, **kwargs)

    async def __aenter__(self) -> Domain:
        self._start = time.perf_counter()
        self._session = await self.resource.start_transaction()
        self.context = self.context_factory(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.resource.end_transaction(self._session, exc_val)
        elapsed = (time.perf_counter() - self._start) * 1000
        logger.info(f"'{self.command_name}' executed in {elapsed:.1f} ms")
