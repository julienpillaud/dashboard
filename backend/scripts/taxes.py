import asyncio
import uuid
from collections import defaultdict

from app.core.context import Context
from app.domain.stores.entities import Store
from app.domain.stores.use_cases import get_stores
from app.domain.taxes.entities import RawTax, Tax
from scripts.commons import build_parser, get_context, logger, setup_logging

TAXES = [0, 5.5, 10, 20]


async def fetch_pos_taxes(
    context: Context,
    /,
    store: Store,
) -> tuple[Store, list[RawTax]]:
    pos_manager = await context.get_pos_manager(store=store)
    raw_taxes = await pos_manager.get_taxes()
    return store, raw_taxes


async def migrate_taxes(context: Context, dry_run: bool) -> None:
    stores = await get_stores(context)

    tasks = [fetch_pos_taxes(context, store) for store in stores]
    results = await asyncio.gather(*tasks)

    taxes_map = defaultdict(dict)
    for store, raw_taxes in results:
        for raw_tax in raw_taxes:
            taxes_map[raw_tax.rate][str(store.id)] = raw_tax

    taxes = []
    for rate, mapping in taxes_map.items():
        if len(mapping) != len(stores):
            logger.warning(f"Exclude tax '{rate}'")
            continue

        if rate not in TAXES:
            logger.warning(f"Exclude tax '{rate}'")
            continue

        tax = Tax(id=uuid.uuid7(), rate=rate, store_mapping=mapping)
        taxes.append(tax)

    assert len(taxes) == len(TAXES)
    logger.info(f"Creating {len(taxes)} taxes")
    if not dry_run:
        await context.database["taxes"].delete_many({})
        await context.tax_repository.save_many(taxes)
    else:
        logger.warning("Dry run: nothing to do")


async def run(database: str, dry_run: bool) -> None:
    context = await get_context(database=database)
    await migrate_taxes(context, dry_run=dry_run)


def main() -> None:
    setup_logging()
    parser = build_parser()
    args = parser.parse_args()
    asyncio.run(run(database=args.database, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
