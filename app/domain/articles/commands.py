import uuid

from cleanstack import (
    FilterEntity,
    PaginatedResponse,
    Pagination,
    SortEntity,
    SortOrder,
)

from app.domain.articles.entities import Article, RawArticle
from app.domain.categories.commands import get_categories_command, get_category_command
from app.domain.context import ContextProtocol
from app.domain.logger import logger
from app.domain.stores.entities import Store
from app.domain.taxes.commands import get_tax_command, get_taxes_command


async def get_raw_articles_command(
    context: ContextProtocol,
    /,
    current_store: Store,
    limit: int = 100,
    skip: int = 0,
) -> list[RawArticle]:
    return await context.pos_manager.get_articles(current_store, limit=limit, skip=skip)


async def get_articles_command(
    context: ContextProtocol,
    /,
    current_store: Store,
) -> PaginatedResponse[Article]:
    return await context.article_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(current_store.id))],
        sort=[SortEntity(field="raw.name", order=SortOrder.ASC)],
        pagination=Pagination(size=3000),
    )


async def synchronize_articles_command(
    context: ContextProtocol,
    /,
    current_store: Store,
) -> None:
    raw_articles = await context.pos_manager.get_articles(current_store, limit=3000)
    raw_articles_ids = {article.id for article in raw_articles}

    articles = await context.article_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(current_store.id))],
        pagination=Pagination(size=3000),
    )
    articles_map = {article.external_id: article for article in articles.items}

    to_create = []
    to_update = []
    for raw_article in raw_articles:
        if raw_article.id not in articles_map:
            logger.info(f"Synchronization: Creating article: {raw_article.name}")
            to_create.append(raw_article)
        else:
            raw_articles_ids.discard(raw_article.id)
            article = articles_map[raw_article.id]
            if article.raw.updated_at != raw_article.updated_at:
                logger.info(f"Synchronization: Updating article: {raw_article.name}")
                to_update.append((article, raw_article))

    if to_create:
        await create_article(context, current_store, to_create=to_create)
    if to_update:
        await update_article(context, current_store, to_update=to_update)


async def create_article(
    context: ContextProtocol,
    /,
    current_store: Store,
    to_create: list[RawArticle],
) -> None:
    categories = await get_categories_command(context, current_store)
    categories_map = {category.external_id: category for category in categories.items}
    taxes = await get_taxes_command(context, current_store)
    taxes_map = {tax.external_id: tax for tax in taxes.items}

    articles: list[Article] = []
    for raw_article in to_create:
        category = categories_map[raw_article.category_id]
        tax = taxes_map[raw_article.taxes[0]]
        article = Article(
            id=uuid.uuid7(),
            store_id=current_store.id,
            external_id=raw_article.id,
            category=category.raw.name,
            tax_rate=tax.raw.rate,
            raw=raw_article,
        )
        articles.append(article)

    await context.article_repository.save_many(articles)


async def update_article(
    context: ContextProtocol,
    /,
    current_store: Store,
    to_update: list[tuple[Article, RawArticle]],
) -> None:
    articles: list[Article] = []
    for article, raw_article in to_update:
        if article.raw.category_id != raw_article.category_id:
            category = await get_category_command(
                context,
                current_store,
                external_id=raw_article.category_id,
            )
            article.category = category.raw.name

        if article.raw.taxes[0] != raw_article.taxes[0]:
            tax = await get_tax_command(
                context,
                current_store,
                external_id=raw_article.taxes[0],
            )
            article.tax_rate = tax.raw.rate

        article.raw = raw_article

        articles.append(article)

    await context.article_repository.save_many(articles)
