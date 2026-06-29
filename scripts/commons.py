import json
import logging.config
from pathlib import Path

import httpx
from cleanstack.mongo import MongoDocument

from app.core.context import Context
from app.core.settings import Settings
from app.domain.stores.entities import Store
from app.infrastructure.mongo.resource import AsyncMongoResource

project_path = Path(__file__).parents[1]


def setup_logging(path: Path) -> None:
    with open(path / "app/core/logging/config-dev.json") as f:
        config = json.load(f)
    logging.config.dictConfig(config)


async def get_context() -> Context:
    settings = Settings(_env_file=project_path / ".env")  # ty:ignore[missing-argument, unknown-argument]
    http_client = httpx.AsyncClient(timeout=settings.http_client_timeout)
    mongo_resource = await AsyncMongoResource.from_settings(settings)
    return Context(
        settings=settings,
        http_client=http_client,
        database=mongo_resource.client[settings.mongo_database],
    )


async def get_stores(context: Context) -> list[Store]:
    response = await context.store_repository.get_all()
    return response.items


async def get_old_articles(database: str) -> list[MongoDocument]:
    settings = Settings(
        _env_file=project_path / ".env",  # ty:ignore[unknown-argument]
        mongo_database=database,
    )  # ty:ignore[missing-argument]
    resource = await AsyncMongoResource.from_settings(settings)
    cursor = resource.database["articles"].find()
    return await cursor.to_list()
