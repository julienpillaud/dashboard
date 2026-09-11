import asyncio
import uuid
from collections import defaultdict

from app.core.context import Context
from app.domain.categories.entities import Category, RawCategory
from app.domain.stores.entities import Store
from scripts.commons import get_stores, logger


async def fetch_pos_categories(
    context: Context,
    /,
    store: Store,
) -> tuple[Store, list[RawCategory]]:
    pos_manager = context.get_pos_manager(store=store)
    raw_categories = await pos_manager.get_categories()
    return store, raw_categories


async def migrate_categories(context: Context, dry_run: bool) -> None:
    stores = await get_stores(context=context)
    if not stores:
        logger.warning("No stores in database")
        return

    tasks = [fetch_pos_categories(context, store) for store in stores]
    results = await asyncio.gather(*tasks)

    categories_by_name = defaultdict(dict)
    for store, raw_categories in results:
        for raw_category in raw_categories:
            categories_by_name[raw_category.name][str(store.id)] = raw_category

    categories = []
    for name, mapping in categories_by_name.items():
        if len(mapping) == len(stores):
            category = Category(id=uuid.uuid7(), name=name, store_mapping=mapping)
            categories.append(category)
            logger.info(f"Creating category {name}")

    if not dry_run:
        await context.database["categories"].delete_many({})
        await context.category_repository.save_many(categories)
    else:
        logger.warning("Dry run: nothing to do")
