import datetime
import uuid

from app.domain.articles.entities import Article, RawArticle
from app.domain.articles.synchronization.entities import ArticleSynchronizationPlan
from app.domain.categories.use_cases import get_categories, get_category_by_external_id
from app.domain.context import ContextProtocol
from app.domain.logger import logger
from app.domain.stores.entities import Store
from app.domain.taxes.use_cases import get_tax_by_external_id, get_taxes


async def persist_synchronization_plan(
    context: ContextProtocol,
    /,
    store: Store,
    plan: ArticleSynchronizationPlan,
) -> None:
    await create_articles(context, store=store, to_create=plan.to_create)
    await update_articles(
        context,
        store=store,
        to_update=[(item.entity, item.raw_entity) for item in plan.to_update],
    )
    await delete_articles(context, to_delete=plan.to_delete)


async def create_articles(
    context: ContextProtocol,
    /,
    store: Store,
    to_create: list[RawArticle],
) -> None:
    if not to_create:
        logger.info("Synchronization: No article to create")
        return

    categories = await get_categories(context, store_slug=store.slug)
    categories_map = {category.raw.id: category for category in categories.items}
    taxes = await get_taxes(context, store_slug=store.slug)
    taxes_map = {tax.raw.id: tax for tax in taxes.items}

    current_time = datetime.datetime.now(datetime.UTC)

    articles: list[Article] = []
    for raw_article in to_create:
        category = categories_map[raw_article.category_id]
        tax = taxes_map[raw_article.taxes[0]]
        article = Article(
            id=uuid.uuid7(),
            store_id=store.id,
            store_name=store.name,
            category=category.raw.name,
            tax_rate=tax.raw.rate,
            raw=raw_article,
            data=None,
            synced_at=current_time,
        )
        articles.append(article)

    await context.article_repository.save_many(articles)


async def update_articles(
    context: ContextProtocol,
    /,
    store: Store,
    to_update: list[tuple[Article, RawArticle]],
) -> None:
    if not to_update:
        logger.info("Synchronization: No article to update")
        return

    current_time = datetime.datetime.now(datetime.UTC)

    articles: list[Article] = []
    for article, raw_article in to_update:
        if article.raw.category_id != raw_article.category_id:
            category = await get_category_by_external_id(
                context,
                store,
                external_id=raw_article.category_id,
            )
            article.category = category.raw.name

        if article.raw.taxes[0] != raw_article.taxes[0]:
            tax = await get_tax_by_external_id(
                context,
                store,
                external_id=raw_article.taxes[0],
            )
            article.tax_rate = tax.raw.rate

        article.raw = raw_article
        article.synced_at = current_time

        articles.append(article)

    await context.article_repository.update_raw(articles)


async def delete_articles(
    context: ContextProtocol,
    /,
    to_delete: list[Article],
) -> None:
    if not to_delete:
        logger.info("Synchronization: No articles to delete")
        return

    await context.article_repository.delete_many(to_delete)
