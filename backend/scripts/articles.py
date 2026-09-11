import asyncio
import datetime
import uuid
from collections import defaultdict
from collections.abc import Sequence
from typing import NamedTuple

from cleanstack.mongo import MongoDocument

from app.core.context import Context
from app.domain.articles.entities import (
    Article,
    ArticleData,
    ArticleDetails,
    PosArticle,
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


async def get_categories_map(context: ContextProtocol, /) -> dict[str, dict[str, str]]:
    categories_map: dict[str, dict[str, str]] = defaultdict(dict)
    categories = await get_categories(context)
    for category in categories.items:
        for store_id, raw_category in category.store_mapping.items():
            categories_map[store_id][raw_category.id] = category.name

    return categories_map


async def get_taxes_map(context: ContextProtocol, /) -> dict[str, dict[str, float]]:
    taxes_map: dict[str, dict[str, float]] = defaultdict(dict)
    taxes = await get_taxes(context)
    for tax in taxes.items:
        for store_id, raw_tax in tax.store_mapping.items():
            taxes_map[store_id][raw_tax.id] = raw_tax.rate

    return taxes_map


async def fetch_pos_articles(
    context: ContextProtocol,
    /,
    store: Store,
    categories_map: dict[str, dict[str, str]],
    taxes_map: dict[str, dict[str, float]],
) -> dict[str, PosFetchResult]:
    pos_manager = context.get_pos_manager(store=store)
    raw_articles = await pos_manager.get_articles(limit=3000)

    output = {}
    for raw_article in raw_articles:
        if not raw_article.reference:
            continue

        output[raw_article.reference] = PosFetchResult(
            store=store,
            raw_article=raw_article,
            category=categories_map[str(store.id)][raw_article.category_id],
            tax_rate=taxes_map[str(store.id)][raw_article.taxes[0]],
        )

    return output


def check_article_consistency(
    old_article: MongoDocument,
    results: Sequence[PosFetchResult],
    length: int,
) -> bool:
    is_consistent = True

    if len(results) != length:
        is_consistent = False
        logger.warning(f"Consistency failed on 'len' for {old_article['name']}")

    checks = [
        ("name", [r.raw_article.name for r in results]),
        ("category", [r.category for r in results]),
        ("tax_rate", [r.tax_rate for r in results]),
    ]
    for field, values in checks:
        if len(set(values)) > 1:
            is_consistent = False
            logger.warning(f"Consistency failed on '{field}' for {old_article['name']}")
            for result, value in zip(results, values, strict=True):
                logger.warning(f"{result.store.name}: {value}")

    return is_consistent


async def get_old_articles(context: Context) -> list[MongoDocument]:
    db_source = context.transaction.client["dashboard"]
    cursor = db_source["articles"].find()
    return await cursor.to_list()


def build_article_data(old_article: MongoDocument) -> ArticleData:
    details = ArticleDetails(
        alcohol_by_volume=empty_to_none(old_article["alcohol_by_volume"]),
        volume=get_volume(old_article),
        origin=get_origin(old_article["region"]),
        color=empty_to_none(old_article["color"]),
        taste=empty_to_none(old_article["taste"]),
        distributor=old_article["distributor"],
    )
    return ArticleData(
        details=details,
        total_cost=get_total_cost(old_article),
        deposit=get_deposit(old_article),
    )


def build_articles(
    old_articles: list[MongoDocument],
    pos_articles: dict[str, list[PosFetchResult]],
    length: int,
) -> list[Article]:
    current_time = datetime.datetime.now(datetime.UTC)
    articles = []
    for old_article in old_articles:
        reference = str(old_article["_id"])
        results = pos_articles.get(reference)
        if not results:
            logger.warning(f"No POS article for {old_article['name']}")
            continue

        if not check_article_consistency(
            old_article=old_article,
            results=results,
            length=length,
        ):
            continue

        first_result = results[0]
        store_mapping = {
            str(result.store.id): PosArticle(
                store_name=result.store.name,
                price=result.raw_article.full_price or 0,
                raw=result.raw_article,
            )
            for result in results
        }
        articles.append(
            Article(
                id=uuid.uuid7(),
                name=first_result.raw_article.name,
                category=first_result.category,
                tax_rate=first_result.tax_rate,
                data=build_article_data(old_article),
                store_mapping=store_mapping,
                created_at=current_time,
                updated_at=current_time,
            )
        )

    return articles


async def migrate_articles(context: Context, dry_run: bool) -> None:
    stores = await get_stores(context)
    if not stores:
        logger.warning("No stores in database")
        return

    categories_map = await get_categories_map(context)
    taxes_map = await get_taxes_map(context)

    tasks = [
        fetch_pos_articles(
            context,
            store=store,
            categories_map=categories_map,
            taxes_map=taxes_map,
        )
        for store in stores
    ]
    fetch_responses = await asyncio.gather(*tasks)

    pos_articles = defaultdict(list)
    for response in fetch_responses:
        for reference, result in response.items():
            pos_articles[reference].append(result)
    logger.info(f"POS articles: {len(pos_articles)}")

    old_articles = await get_old_articles(context=context)
    logger.info(f"Old articles: {len(old_articles)}")

    articles = build_articles(
        old_articles=old_articles,
        pos_articles=pos_articles,
        length=len(stores),
    )

    if not dry_run:
        await context.database["articles"].delete_many({})
        await context.article_repository.save_many(articles)
    else:
        logger.warning("Dry run: nothing to do")
