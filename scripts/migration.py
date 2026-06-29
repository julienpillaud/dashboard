import asyncio
import datetime
import logging.config
import uuid
from pathlib import Path
from typing import NamedTuple

from cleanstack.mongo import MongoDocument

from app.core.context import Context
from app.domain.articles.entities import (
    Article,
    ArticleData,
    ArticleDetails,
    RawArticle,
)
from app.domain.categories.commands import get_categories_command
from app.domain.stores.entities import Store
from app.domain.taxes.commands import get_taxes_command
from scripts.commons import (
    get_context,
    get_old_articles,
    get_stores,
    setup_logging,
)
from scripts.utils import (
    empty_to_none,
    get_deposit,
    get_origin,
    get_total_cost,
    get_volume,
)

logger = logging.getLogger("app.migration")
project_path = Path(__file__).parents[1]


class PosFetchResult(NamedTuple):
    store: Store
    raw_article: RawArticle
    category: str
    tax_rate: float


async def fetch_pos_articles(
    context: Context,
    store: Store,
    old_articles_map: dict[str, MongoDocument],
) -> dict[str, PosFetchResult]:
    pos_manager = context.get_pos_manager(store=store)
    raw_articles = await pos_manager.get_articles(limit=3000)

    categories = await get_categories_command(context, store_slug=store.slug)
    categories_map = {category.raw.id: category for category in categories.items}
    taxes = await get_taxes_command(context, store_slug=store.slug)
    taxes_map = {tax.raw.id: tax for tax in taxes.items}

    output = {}
    for raw_article in raw_articles:
        if not raw_article.reference or raw_article.reference not in old_articles_map:
            logger.warning(f"Article not found: {raw_article.name} ({store.name})")

        output_key = raw_article.reference or f"NO_REF_{raw_article.id}"
        output[output_key] = PosFetchResult(
            store=store,
            raw_article=raw_article,
            category=categories_map[raw_article.category_id].raw.name,
            tax_rate=taxes_map[raw_article.taxes[0]].raw.rate,
        )

    return output


async def main() -> None:
    setup_logging(project_path)
    context = await get_context()
    stores = await get_stores(context)

    old_articles = await get_old_articles("dashboard")
    old_articles_map = {}
    for old_article in old_articles:
        old_article["internal_id"] = uuid.uuid7()
        old_articles_map[str(old_article["_id"])] = old_article

    tasks = [fetch_pos_articles(context, store, old_articles_map) for store in stores]
    pos_articles = await asyncio.gather(*tasks)

    flat_pos_articles = [
        (reference, result)
        for store_map in pos_articles
        for reference, result in store_map.items()
    ]

    current_time = datetime.datetime.now(datetime.UTC)
    to_create = []
    for reference, result in flat_pos_articles:
        old_article = old_articles_map.get(reference)
        article = Article(
            id=uuid.uuid7(),
            store_id=result.store.id,
            category=result.category,
            tax_rate=result.tax_rate,
            raw=result.raw_article,
            data=ArticleData(
                internal_id=old_article["internal_id"],
                details=ArticleDetails(
                    alcohol_by_volume=empty_to_none(old_article["alcohol_by_volume"]),
                    volume=get_volume(old_article),
                    origin=get_origin(old_article["region"]),
                    color=empty_to_none(old_article["color"]),
                    taste=empty_to_none(old_article["taste"]),
                    distributor=old_article["distributor"],
                ),
                total_cost=get_total_cost(old_article),
                deposit=get_deposit(old_article),
                enhanced_at=current_time,
            )
            if old_article
            else None,
            synced_at=current_time,
        )
        to_create.append(article)

    await context.article_repository.save_many(to_create)


if __name__ == "__main__":
    asyncio.run(main())
