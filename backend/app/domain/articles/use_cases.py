import asyncio
import datetime
import uuid

from cleanstack import (
    EntityId,
    FilterEntity,
    PaginatedResponse,
    Pagination,
    SortEntity,
    SortOrder,
)

from app.domain.articles.entities import (
    Article,
    ArticleInput,
    ArticleSynchronizationResult,
    RawArticle,
)
from app.domain.articles.utils import (
    create_pos_article,
    fetch_pos_articles,
    get_article_references,
    update_pos_article,
)
from app.domain.context import ContextProtocol
from app.domain.exceptions import NotFoundError
from app.domain.stores.entities import Store
from app.domain.stores.use_cases import get_stores


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


async def create_article(
    context: ContextProtocol,
    /,
    data: ArticleInput,
) -> Article:
    references = await get_article_references(context, data=data)

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

    # Create POS articles
    results = await asyncio.gather(
        *(
            create_pos_article(
                context,
                store=store,
                category=references.category,
                tax=references.tax,
                name=article.name,
                price=data.prices[store.id],
                reference=article.id.hex,
            )
            for store in references.stores
        )
    )

    # Fill article with POS results
    for store, result in zip(references.stores, results, strict=True):
        article.add_store_mapping(
            store=store,
            price=data.prices[store.id],
            result=result,
        )

    await context.article_repository.save(article)
    return article


async def update_article(
    context: ContextProtocol,
    /,
    article_id: EntityId,
    data: ArticleInput,
) -> Article:
    article = await context.article_repository.get_by_id(article_id)
    if not article:
        raise NotFoundError(f"Article '{article_id}' not found")

    references = await get_article_references(context, data=data)
    has_pos_changes = article.has_pos_changes(data)

    # Only call the POS for stores that need it
    # Stores where the creation failed (no raw) are skipped:
    # retrying the creation is not handled here
    targets: list[tuple[Store, RawArticle]] = []
    for store in references.stores:
        pos_article = article.store_mapping[str(store.id)]
        if pos_article.raw and pos_article.needs_update(
            price=data.prices[store.id],
            has_pos_changes=has_pos_changes,
        ):
            targets.append((store, pos_article.raw))

    # Update POS articles
    results = await asyncio.gather(
        *(
            update_pos_article(
                context,
                article_id=raw_article.id,
                store=store,
                category=references.category,
                tax=references.tax,
                name=data.name,
                price=data.prices[store.id],
                reference=article.id.hex,
            )
            for store, raw_article in targets
        )
    )

    # Update article in DB
    article.apply_input(data=data, current_time=datetime.datetime.now(datetime.UTC))

    # Fill article with POS results
    for (store, _), result in zip(targets, results, strict=True):
        article.update_store_mapping(
            store=store,
            price=data.prices[store.id],
            result=result,
        )

    await context.article_repository.update(article)
    return article


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
            article.synchronize_store_mapping(updated_raws)
            updated_articles.append(article)

    await context.article_repository.update_many(updated_articles)
    return ArticleSynchronizationResult(
        updated=len(updated_articles),
        failed_stores=failed_stores,
    )
