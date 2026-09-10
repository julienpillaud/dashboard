import asyncio

from app.core.context import Context
from app.domain.taxes.use_cases import synchronize_taxes
from scripts.commons import get_stores, logger


async def migrate_taxes(context: Context, dry_run: bool) -> None:
    stores = await get_stores(context=context)
    if not stores:
        logger.warning("No stores in database")
        return

    if not dry_run:
        await context.database["taxes"].delete_many({})
        tasks = [
            synchronize_taxes(context, store_slug=store.slug, dry_run=False)
            for store in stores
        ]
        await asyncio.gather(*tasks)
    else:
        logger.warning("Dry run: nothing to do")
