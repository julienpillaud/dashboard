import datetime
import uuid

from app.domain.articles.entities import Article, RawArticle
from app.domain.categories.commands import get_categories_command, get_category_command
from app.domain.context import ContextProtocol
from app.domain.stores.entities import Store
from app.domain.taxes.commands import get_tax_command, get_taxes_command


async def create_articles(
    context: ContextProtocol,
    /,
    store: Store,
    to_create: list[RawArticle],
) -> None:
    categories = await get_categories_command(context, store_slug=store.slug)
    categories_map = {category.raw.id: category for category in categories.items}
    taxes = await get_taxes_command(context, store_slug=store.slug)
    taxes_map = {tax.raw.id: tax for tax in taxes.items}

    current_time = datetime.datetime.now(datetime.UTC)

    articles: list[Article] = []
    for raw_article in to_create:
        category = categories_map[raw_article.category_id]
        tax = taxes_map[raw_article.taxes[0]]
        article = Article(
            id=uuid.uuid7(),
            store_id=store.id,
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
    current_time = datetime.datetime.now(datetime.UTC)

    articles: list[Article] = []
    for article, raw_article in to_update:
        if article.raw.category_id != raw_article.category_id:
            category = await get_category_command(
                context,
                store,
                external_id=raw_article.category_id,
            )
            article.category = category.raw.name

        if article.raw.taxes[0] != raw_article.taxes[0]:
            tax = await get_tax_command(
                context,
                store,
                external_id=raw_article.taxes[0],
            )
            article.tax_rate = tax.raw.rate

        article.raw = raw_article
        article.synced_at = current_time

        articles.append(article)

    await context.article_repository.update_raw(articles)
