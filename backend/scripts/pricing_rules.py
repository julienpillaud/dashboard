import uuid

from app.core.context import Context
from app.domain.categories.use_cases import get_categories
from app.domain.pricing.entities import PricingRule
from app.domain.stores.use_cases import get_stores
from scripts.commons import logger
from scripts.data.pricing_configs import PRICING_CONFIGS_MAP


async def migrate_pricing_rules(context: Context, dry_run: bool) -> None:
    stores = await get_stores(context)
    categories = await get_categories(context)

    pricing_rules = []
    for store in stores:
        for category in categories:
            logger.info(f"Creating pricing rules {store.name}-{category.name}")
            pricing_rules.append(
                PricingRule(
                    id=uuid.uuid7(),
                    store_id=store.id,
                    category_id=category.id,
                    pricing_config=PRICING_CONFIGS_MAP[category.name],
                )
            )

    if not dry_run:
        await context.database["pricing_rules"].delete_many({})
        await context.pricing_rules_repository.save_many(pricing_rules)
    else:
        logger.warning("Dry run: nothing to do")
