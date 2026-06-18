from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

import httpx
from fastapi import FastAPI

from app.api.logger import logger
from app.core.settings import Settings
from app.infrastructure.mongo.resource import AsyncMongoResource


def lifespan_factory(
    settings: Settings,
) -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.mongo_resource = await AsyncMongoResource.from_settings(settings)
        app.state.http_client = httpx.AsyncClient(timeout=settings.http_client_timeout)
        logger.info("Application startup complete")

        yield

        await app.state.http_client.aclose()
        await app.state.mongo_resource.release()
        logger.info("Application shutdown complete")

    return lifespan
