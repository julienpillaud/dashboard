import asyncio

from app.core.context import Context
from app.domain.categories.use_cases import synchronize_categories
from scripts.commons import get_stores, logger


async def migrate_categories(context: Context, dry_run: bool) -> None:
    stores = await get_stores(context=context)
    if not stores:
        logger.warning("No stores in database")
        return

    if not dry_run:
        await context.database["categories"].delete_many({})
        tasks = [
            synchronize_categories(context, store_slug=store.slug, dry_run=False)
            for store in stores
        ]
        await asyncio.gather(*tasks)
    else:
        logger.warning("Dry run: nothing to do")
