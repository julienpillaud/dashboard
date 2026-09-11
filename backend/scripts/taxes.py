import asyncio
import uuid
from collections import defaultdict

from app.core.context import Context
from app.domain.stores.entities import Store
from app.domain.taxes.entities import RawTax, Tax
from scripts.commons import get_stores, logger


async def fetch_pos_taxes(
    context: Context,
    /,
    store: Store,
) -> tuple[Store, list[RawTax]]:
    pos_manager = context.get_pos_manager(store=store)
    raw_taxes = await pos_manager.get_taxes()
    return store, raw_taxes


async def migrate_taxes(context: Context, dry_run: bool) -> None:
    stores = await get_stores(context=context)
    if not stores:
        logger.warning("No stores in database")
        return

    tasks = [fetch_pos_taxes(context, store) for store in stores]
    results = await asyncio.gather(*tasks)

    taxes_by_rate = defaultdict(dict)
    for store, raw_taxes in results:
        for raw_tax in raw_taxes:
            taxes_by_rate[raw_tax.rate][str(store.id)] = raw_tax

    taxes = []
    for rate, mapping in taxes_by_rate.items():
        if len(mapping) == len(stores):
            tax = Tax(id=uuid.uuid7(), rate=rate, store_mapping=mapping)
            taxes.append(tax)
            logger.info(f"Creating tax {rate}")

    if not dry_run:
        await context.database["taxes"].delete_many({})
        await context.tax_repository.save_many(taxes)
    else:
        logger.warning("Dry run: nothing to do")
