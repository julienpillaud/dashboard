import asyncio
import uuid
from pathlib import Path

import httpx2

from app.core.context import Context
from app.core.settings import Settings
from app.domain.stores.entities import Store
from app.infrastructure.mongo.resource.asynchronous import (
    MongoResource,
    MongoTransaction,
)

project_path = Path(__file__).parents[1]


async def get_context(settings: Settings) -> Context:
    http_client = httpx2.AsyncClient(timeout=settings.http_client_timeout)
    mongo_resource = await MongoResource.from_settings(settings)
    mongo_transaction = MongoTransaction(mongo_resource)
    return Context(
        settings=settings,
        http_client=http_client,
        transaction=mongo_transaction,
    )


async def main() -> None:
    settings = Settings(_env_file=project_path / ".env")
    context = await get_context(settings=settings)

    db_source = context.transaction.client["dashboard"]

    cursor = db_source["shops"].find()
    previous_stores = await cursor.to_list()
    for previous_store in previous_stores:
        store = Store(
            id=uuid.uuid7(),
            name=previous_store["name"],
            slug=previous_store["username"],
            tactill_api_key=previous_store["tactill_api_key"],
        )
        await context.store_repository.save(store)


if __name__ == "__main__":
    asyncio.run(main())
