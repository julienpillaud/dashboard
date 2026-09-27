import asyncio
import uuid
from collections import defaultdict

from app.core.context import Context
from app.domain.categories.entities import Category, RawCategory
from app.domain.stores.entities import Store
from app.domain.stores.use_cases import get_stores
from scripts.commons import build_parser, get_context, logger, setup_logging
from scripts.data.categories import CATEGORIES_MAP


async def fetch_pos_categories(
    context: Context,
    /,
    store: Store,
) -> tuple[Store, list[RawCategory]]:
    pos_manager = await context.get_pos_manager(store=store)
    raw_categories = await pos_manager.get_categories()
    return store, raw_categories


async def migrate_categories(context: Context, dry_run: bool) -> None:
    stores = await get_stores(context)

    tasks = [fetch_pos_categories(context, store) for store in stores]
    results = await asyncio.gather(*tasks)

    categories_map = defaultdict(dict)
    for store, raw_categories in results:
        for raw_category in raw_categories:
            categories_map[raw_category.name][str(store.id)] = raw_category

    categories = []
    for name, mapping in categories_map.items():
        if len(mapping) != len(stores):
            logger.warning(f"Exclude category '{name}'")
            continue

        fields = CATEGORIES_MAP.get(name)
        if not fields:
            logger.warning(f"Exclude category '{name}'")
            continue

        category = Category(
            id=uuid.uuid7(),
            name=name,
            fields=fields,
            store_mapping=mapping,
        )
        categories.append(category)

    assert len(categories) == len(CATEGORIES_MAP)
    logger.info(f"Creating {len(categories)} categories")
    if not dry_run:
        await context.database["categories"].delete_many({})
        await context.category_repository.save_many(categories)
    else:
        logger.warning("Dry run: nothing to do")


async def run(database: str, dry_run: bool) -> None:
    context = await get_context(database=database)
    await migrate_categories(context, dry_run=dry_run)


def main() -> None:
    setup_logging()
    parser = build_parser()
    args = parser.parse_args()
    asyncio.run(run(database=args.database, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
