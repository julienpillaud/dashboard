import asyncio
import datetime
import uuid
from decimal import Decimal

from cleanstack import (
    FilterEntity,
    PaginatedResponse,
    Pagination,
    SortEntity,
    SortOrder,
)

from app.domain.articles.entities import (
    Article,
    ArticleCreate,
    ArticleSynchronizationResult,
    POSAPIResult,
    POSStatus,
    RawArticle,
)
from app.domain.categories.entities import Category
from app.domain.context import ContextProtocol
from app.domain.exceptions import NotFoundError
from app.domain.logger import logger
from app.domain.protocols import (
    POSError,
)
from app.domain.stores.entities import Store
from app.domain.stores.use_cases import get_stores
from app.domain.taxes.entities import Tax


async def get_articles(
    context: ContextProtocol,
    /,
    search: str | None = None,
    filters: list[FilterEntity] | None = None,
    pagination: Pagination | None = None,
) -> PaginatedResponse[Article]:
    return await context.article_repository.get_all(
        search=search,
        filters=filters,
        sort=[
            SortEntity(field="category", order=SortOrder.ASC),
            SortEntity(field="name", order=SortOrder.ASC),
        ],
        pagination=pagination,
    )


async def create_article(context: ContextProtocol, /, data: ArticleCreate) -> Article:
    category = await context.category_repository.get_by_name(name=data.category)
    if not category:
        raise NotFoundError(f"Category {data.category} not found")

    tax = await context.tax_repository.get_by_rate(rate=data.tax_rate)
    if not tax:
        raise NotFoundError(f"Tax {data.tax_rate} not found")

    stores = await get_stores(context)

    current_time = datetime.datetime.now(datetime.UTC)
    article = Article(
        id=uuid.uuid7(),
        name=data.name,
        category=data.category,
        total_cost=data.total_cost,
        tax_rate=data.tax_rate,
        distributor=data.distributor,
        details=data.details,
        created_at=current_time,
        updated_at=current_time,
    )

    results = await asyncio.gather(
        *(
            create_pos_article(
                context,
                store=store,
                category=category,
                tax=tax,
                price=data.price,
                article=article,
            )
            for store in stores
        )
    )
    for store, result in zip(stores, results, strict=True):
        article.add_store_mapping(store=store, price=data.price, result=result)

    await context.article_repository.save(article)
    return article


async def create_pos_article(
    context: ContextProtocol,
    /,
    store: Store,
    category: Category,
    tax: Tax,
    price: Decimal,
    article: Article,
) -> POSAPIResult[RawArticle]:
    manager = await context.get_pos_manager(store)
    category_id = category.store_mapping[str(store.id)].id
    tax_id = tax.store_mapping[str(store.id)].id

    try:
        raw_article = await manager.create_article(
            category_id=category_id,
            tax_id=tax_id,
            price=price,
            article=article,
        )
    except POSError as error:
        return POSAPIResult(status=POSStatus.FAILED, data=None, error=str(error))

    return POSAPIResult(status=POSStatus.CREATED, data=raw_article, error=None)


async def synchronize_articles(
    context: ContextProtocol,
    /,
) -> ArticleSynchronizationResult:
    stores = await get_stores(context)
    results = await asyncio.gather(
        *(fetch_pos_articles(context, store=store) for store in stores)
    )

    failed_stores = []
    raws_by_store = {}
    for store, result in zip(stores, results, strict=True):
        if result is None:
            failed_stores.append(store.slug)
            continue

        raws_by_store[str(store.id)] = {raw.id: raw for raw in result}

    articles = await context.article_repository.get_all(
        pagination=Pagination(size=3000)
    )
    updated_articles = []
    for article in articles.items:
        updated_raws = {}
        for store_id, pos_article in article.store_mapping.items():
            if pos_article.raw is None:
                continue

            raw = raws_by_store.get(store_id, {}).get(pos_article.raw.id)
            if raw is None:
                continue

            if pos_article.raw != raw:
                updated_raws[store_id] = raw

        if updated_raws:
            article.update_store_mapping(updated_raws)
            updated_articles.append(article)

    await context.article_repository.update_many(updated_articles)
    return ArticleSynchronizationResult(
        updated=len(updated_articles),
        failed_stores=failed_stores,
    )


async def fetch_pos_articles(
    context: ContextProtocol,
    /,
    store: Store,
) -> list[RawArticle] | None:
    manager = await context.get_pos_manager(store)
    try:
        return await manager.get_articles(limit=3000)
    except POSError as error:
        logger.warning(f"Failed to fetch articles for store {store.name}: {error}")
        return None
