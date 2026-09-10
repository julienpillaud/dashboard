import asyncio
import datetime
import uuid
from collections import defaultdict
from typing import NamedTuple

from cleanstack import EntityId
from cleanstack.mongo import MongoDocument

from app.core.context import Context
from app.domain.articles.entities import (
    Article,
    ArticleData,
    ArticleDetails,
    RawArticle,
)
from app.domain.categories.use_cases import get_categories
from app.domain.context import ContextProtocol
from app.domain.stores.entities import Store
from app.domain.taxes.use_cases import get_taxes
from scripts.commons import (
    get_stores,
    logger,
)
from scripts.utils import (
    empty_to_none,
    get_deposit,
    get_origin,
    get_total_cost,
    get_volume,
)


class PosFetchResult(NamedTuple):
    store: Store
    raw_article: RawArticle
    category: str
    tax_rate: float


async def fetch_pos_articles(
    context: ContextProtocol,
    /,
    store: Store,
) -> dict[str, PosFetchResult]:
    pos_manager = context.get_pos_manager(store=store)
    raw_articles = await pos_manager.get_articles(limit=3000)

    categories = await get_categories(context, store_slug=store.slug)
    categories_map = {category.raw.id: category for category in categories.items}
    taxes = await get_taxes(context, store_slug=store.slug)
    taxes_map = {tax.raw.id: tax for tax in taxes.items}

    output = {}
    for raw_article in raw_articles:
        output_key = raw_article.reference or f"NO_REF_{raw_article.id}"
        output[output_key] = PosFetchResult(
            store=store,
            raw_article=raw_article,
            category=categories_map[raw_article.category_id].raw.name,
            tax_rate=taxes_map[raw_article.taxes[0]].raw.rate,
        )

    return output


async def get_old_articles(context: Context) -> list[MongoDocument]:
    db_source = context.transaction.client["dashboard"]
    cursor = db_source["articles"].find()
    return await cursor.to_list()


async def build_old_articles_map(context: Context) -> dict[str, MongoDocument]:
    old_articles = await get_old_articles(context=context)
    old_articles_map = {}
    for old_article in old_articles:
        old_article["internal_id"] = uuid.uuid7()
        old_articles_map[str(old_article["_id"])] = old_article

    return old_articles_map


def build_group_ids(
    pos_articles: list[tuple[str, PosFetchResult]],
) -> dict[str, EntityId]:
    references = set()
    by_name_category = defaultdict(list)
    for reference, result in pos_articles:
        if not reference.startswith("NO_REF_"):
            references.add(reference)
        else:
            key = (result.raw_article.name, result.category)
            by_name_category[key].append(reference)

    group_ids = {reference: uuid.uuid7() for reference in references}

    for refs in by_name_category.values():
        group_id = uuid.uuid7()
        for ref in refs:
            group_ids[ref] = group_id

    return group_ids


def build_articles(
    pos_articles: list[tuple[str, PosFetchResult]],
    old_articles_map: dict[str, MongoDocument],
    group_ids: dict[str, EntityId],
) -> list[Article]:
    current_time = datetime.datetime.now(datetime.UTC)
    to_create = []
    for reference, result in pos_articles:
        old_article = old_articles_map.get(reference)
        article = Article(
            id=uuid.uuid7(),
            store_id=result.store.id,
            store_name=result.store.name,
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
            group_id=group_ids[reference],
        )
        to_create.append(article)

    return to_create


async def migrate_articles(context: Context, dry_run: bool) -> None:
    stores = await get_stores(context)
    if not stores:
        logger.warning("No stores in database")
        return

    tasks = [fetch_pos_articles(context, store=store) for store in stores]
    fetch_responses = await asyncio.gather(*tasks)
    pos_articles = [
        (reference, result)
        for response in fetch_responses
        for reference, result in response.items()
    ]
    logger.info(f"POS articles: {len(pos_articles)}")

    group_ids = build_group_ids(pos_articles=pos_articles)
    old_articles_map = await build_old_articles_map(context=context)
    logger.info(f"Old articles: {len(old_articles_map)}")
    articles = build_articles(
        pos_articles=pos_articles,
        old_articles_map=old_articles_map,
        group_ids=group_ids,
    )

    if not dry_run:
        await context.database["articles"].delete_many({})
        await context.article_repository.save_many(articles)
    else:
        logger.warning("Dry run: nothing to do")
