import json
import logging.config
from pathlib import Path

import httpx2

from app.core.context import Context
from app.core.settings import Settings
from app.domain.context import ContextProtocol
from app.domain.stores.entities import Store
from app.infrastructure.mongo.resource.asynchronous import (
    MongoResource,
    MongoTransaction,
)

logger = logging.getLogger("app.migration")
project_path = Path(__file__).parents[1]


def setup_logging() -> None:
    with open(project_path / "app/core/logging/config-dev.json") as f:
        config = json.load(f)
    logging.config.dictConfig(config)


def get_settings(database: str) -> Settings:
    return Settings(_env_file=project_path / ".env", mongo_database=database)


async def get_context(database: str) -> Context:
    settings = get_settings(database=database)
    http_client = httpx2.AsyncClient(timeout=settings.http_client_timeout)
    mongo_resource = await MongoResource.from_settings(settings)
    mongo_transaction = MongoTransaction(mongo_resource)
    return Context(
        settings=settings,
        http_client=http_client,
        transaction=mongo_transaction,
    )


async def get_stores(context: ContextProtocol) -> list[Store]:
    response = await context.store_repository.get_all()
    return response.items
