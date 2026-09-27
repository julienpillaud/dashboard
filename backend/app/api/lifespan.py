from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

import httpx2
from fastapi import FastAPI

from app.core.logger import logger
from app.core.settings import Settings
from app.infrastructure.mongo.resource.asynchronous import MongoResource
from app.infrastructure.tactill.factory import TactillClientFactory


def lifespan_factory(
    settings: Settings,
) -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.mongo_resource = await MongoResource.from_settings(settings)
        app.state.http_client = httpx2.AsyncClient(timeout=settings.http_client_timeout)
        app.state.tactill_factory = TactillClientFactory(
            http_client=app.state.http_client
        )
        logger.info("Application startup complete")

        yield

        await app.state.http_client.aclose()
        await app.state.mongo_resource.release()
        logger.info("Application shutdown complete")

    return lifespan
