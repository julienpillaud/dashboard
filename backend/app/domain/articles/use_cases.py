from cleanstack import (
    FilterEntity,
    PaginatedResponse,
    Pagination,
    SortEntity,
    SortOrder,
)

from app.domain.articles.entities import Article
from app.domain.articles.utils import create_articles, delete_articles, update_articles
from app.domain.context import ContextProtocol
from app.domain.exceptions import NotFoundError
from app.domain.logger import logger
from app.domain.synchronization import (
    SynchronizationResponse,
    build_synchronization_response,
)


async def get_articles(
    context: ContextProtocol,
    /,
    store_slug: str | None = None,
    filters: list[FilterEntity] | None = None,
    pagination: Pagination | None = None,
) -> PaginatedResponse[Article]:
    repo_filters = []
    if store_slug:
        store = await context.store_repository.get_by_slug(slug=store_slug)
        if not store:
            raise NotFoundError("Store not found")
        repo_filters.append(FilterEntity(field="store_id", value=str(store.id)))

    if filters:
        repo_filters.extend(filters)

    return await context.article_repository.get_all(
        filters=repo_filters,
        sort=[SortEntity(field="raw.name", order=SortOrder.ASC)],
        pagination=pagination,
    )


async def synchronize_articles(
    context: ContextProtocol,
    /,
    store_slug: str,
    dry_run: bool = True,
) -> SynchronizationResponse:
    store = await context.store_repository.get_by_slug(slug=store_slug)
    if not store:
        raise NotFoundError("Store not found")

    pos_manager = context.get_pos_manager(store=store)
    raw_articles = await pos_manager.get_articles(limit=3000)
    raw_ids = {category.id for category in raw_articles}

    response = await context.article_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(store.id))],
        pagination=Pagination(size=3000),
    )
    articles_map = {article.raw.id: article for article in response.items}

    to_create = []
    to_update = []
    to_delete = []

    for raw_article in raw_articles:
        if raw_article.id not in articles_map:
            logger.info(f"Synchronization: Creating article: {raw_article.name}")
            to_create.append(raw_article)
        else:
            article = articles_map[raw_article.id]
            if (
                article.raw.updated_at != raw_article.updated_at
                or article.raw.stock_quantity != raw_article.stock_quantity
            ):
                logger.info(f"Synchronization: Updating article: {raw_article.name}")
                to_update.append((article, raw_article))

    for article_raw_id, article in articles_map.items():
        if article_raw_id not in raw_ids:
            logger.info(f"Synchronization: Deleting article: {article.raw.name}")
            to_delete.append(article)

    if not dry_run:
        await create_articles(context, store, to_create=to_create)
        await update_articles(context, store, to_update=to_update)
        await delete_articles(context, to_delete=to_delete)

    return build_synchronization_response(
        dry_run=dry_run,
        store_slug=store_slug,
        raw_items_count=len(raw_articles),
        items_count=len(articles_map),
        to_create=to_create,
        to_update=[item for _, item in to_update],
        to_delete=[item.raw for item in to_delete],
    )
