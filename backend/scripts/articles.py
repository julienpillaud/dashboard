import asyncio
import datetime
import uuid
from collections import defaultdict
from collections.abc import Sequence
from typing import Any, NamedTuple

from cleanstack.mongo import MongoDocument

from app.core.context import Context
from app.domain.articles.entities import (
    Article,
    ArticleDetails,
    PosArticle,
    POSStatus,
    RawArticle,
)
from app.domain.categories.use_cases import get_categories
from app.domain.context import ContextProtocol
from app.domain.origins.entities import Origin
from app.domain.origins.use_cases import get_origins
from app.domain.stores.entities import Store
from app.domain.stores.use_cases import get_stores
from app.domain.taxes.use_cases import get_taxes
from scripts.commons import logger
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
    tax_rate: float
    category_name: str


async def get_taxes_map(context: ContextProtocol, /) -> dict[str, dict[str, float]]:
    taxes_map: dict[str, dict[str, float]] = defaultdict(dict)
    taxes = await get_taxes(context)
    for tax in taxes:
        for store_id, raw_tax in tax.store_mapping.items():
            taxes_map[store_id][raw_tax.id] = raw_tax.rate

    return taxes_map


async def get_categories_map(context: ContextProtocol, /) -> dict[str, dict[str, str]]:
    categories_map: dict[str, dict[str, str]] = defaultdict(dict)
    categories = await get_categories(context)
    for category in categories:
        for store_id, raw_category in category.store_mapping.items():
            categories_map[store_id][raw_category.id] = category.name

    return categories_map


async def fetch_pos_articles(
    context: ContextProtocol,
    /,
    store: Store,
    taxes_map: dict[str, dict[str, float]],
    categories_map: dict[str, dict[str, str]],
) -> dict[str, PosFetchResult]:
    pos_manager = await context.get_pos_manager(store=store)
    raw_articles = await pos_manager.get_articles(limit=3000)

    output = {}
    for raw_article in raw_articles:
        if not raw_article.reference:
            continue

        output[raw_article.reference] = PosFetchResult(
            store=store,
            raw_article=raw_article,
            tax_rate=taxes_map[str(store.id)][raw_article.taxes[0]],
            category_name=categories_map[str(store.id)][raw_article.category_id],
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

    checks: list[tuple[str, list[Any]]] = [
        ("name", [r.raw_article.name for r in results]),
        ("category", [r.category_name for r in results]),
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
    db_source = context.resource.client["dashboard"]
    cursor = db_source["articles"].find()
    return await cursor.to_list()


def build_article_details(
    old_article: MongoDocument,
    origins_map: dict[str, Origin],
) -> ArticleDetails:
    return ArticleDetails(
        origin=get_origin(old_article["region"], origins_map),
        color=empty_to_none(old_article["color"]),
        taste=empty_to_none(old_article["taste"]),
        volume=get_volume(old_article),
        alcohol_by_volume=empty_to_none(old_article["alcohol_by_volume"]),
        deposit=get_deposit(old_article),
    )


def build_articles(
    old_articles: list[MongoDocument],
    pos_articles: dict[str, list[PosFetchResult]],
    origins_map: dict[str, Origin],
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
                status=POSStatus.CREATED,
                raw=result.raw_article,
                error=None,
            )
            for result in results
        }
        articles.append(
            Article(
                id=uuid.uuid7(),
                name=first_result.raw_article.name,
                category=first_result.category_name,
                total_cost=get_total_cost(old_article),
                tax_rate=first_result.tax_rate,
                distributor=old_article["distributor"],
                details=build_article_details(
                    old_article=old_article, origins_map=origins_map
                ),
                store_mapping=store_mapping,
                created_at=current_time,
                updated_at=current_time,
            )
        )

    return articles


async def migrate_articles(context: Context, /, dry_run: bool) -> None:
    stores = await get_stores(context)
    taxes_map = await get_taxes_map(context)
    categories_map = await get_categories_map(context)

    tasks = [
        fetch_pos_articles(
            context,
            store=store,
            taxes_map=taxes_map,
            categories_map=categories_map,
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

    origins = await get_origins(context)
    origins_map = {origin.name: origin for origin in origins}
    articles = build_articles(
        old_articles=old_articles,
        pos_articles=pos_articles,
        origins_map=origins_map,
        length=len(stores),
    )

    if not dry_run:
        await context.database["articles"].delete_many({})
        await context.article_repository.save_many(articles)
    else:
        logger.warning("Dry run: nothing to do")
