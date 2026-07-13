import logging
import time
from collections.abc import Awaitable, Callable
from types import TracebackType
from typing import Concatenate, Protocol

from app.domain.context import ContextProtocol

logger = logging.getLogger("app")


class ResourceProtocol[T](Protocol):
    async def start_transaction(self, transactional: bool) -> T: ...

    async def end_transaction(
        self,
        session: T,
        exc_val: BaseException | None,
        transactional: bool,
    ) -> None: ...


class Domain:
    def __init__(self, context: ContextProtocol) -> None:
        self.context = context
        self.use_case_timings: list[tuple[str, float]] = []

    async def run[**P, R](
        self,
        func: Callable[Concatenate[ContextProtocol, P], Awaitable[R]],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        name = getattr(func, "__name__", "unknown")
        start = time.perf_counter()
        try:
            return await func(self.context, *args, **kwargs)
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            self.use_case_timings.append((name, elapsed))


class BaseDomain[T]:
    def __init__(
        self,
        resource: ResourceProtocol[T],
        context_provider: Callable[[T], ContextProtocol],
        transactional: bool = False,
    ) -> None:
        self._resource = resource
        self._context_provider = context_provider
        self._transactional = transactional

    async def __aenter__(self) -> Domain:
        self._start_time = time.perf_counter()
        logger.info("Enter Domain")

        self._session = await self._resource.start_transaction(
            transactional=self._transactional
        )
        self._context = self._context_provider(self._session)
        self._bound_domain = Domain(context=self._context)
        return self._bound_domain

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:

        await self._resource.end_transaction(
            session=self._session,
            exc_val=exc_val,
            transactional=self._transactional,
        )

        total_elapsed = (time.perf_counter() - self._start_time) * 1000
        for name, elapsed in self._bound_domain.use_case_timings:
            logger.info(f"{name} [{elapsed:.1f} ms]")
        logger.info(f"total [{total_elapsed:.1f} ms]")
        logger.info("Exit Domain")
