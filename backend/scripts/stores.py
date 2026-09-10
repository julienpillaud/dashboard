import uuid

from cleanstack.mongo import MongoDocument

from app.core.context import Context
from app.domain.stores.entities import Store
from scripts.commons import logger


async def get_old_stores(context: Context) -> list[MongoDocument]:
    db_source = context.transaction.client["dashboard"]
    cursor = db_source["shops"].find()
    return await cursor.to_list()


async def migrate_stores(context: Context, dry_run: bool) -> None:
    old_stores = await get_old_stores(context=context)
    stores = [
        Store(
            id=uuid.uuid7(),
            name=old_store["name"],
            slug=old_store["username"],
            tactill_api_key=old_store["tactill_api_key"],
        )
        for old_store in old_stores
    ]

    if not dry_run:
        await context.database["stores"].delete_many({})
        for store in stores:
            logger.info(f"Creating {store.name}")
        await context.store_repository.save_many(stores)
    else:
        logger.warning("Dry run: nothing to do")
