from decimal import Decimal
from typing import NamedTuple

from app.domain.articles.entities import (
    ArticleInput,
    POSAPIResult,
    POSResultStatus,
    RawArticle,
)
from app.domain.categories.entities import Category
from app.domain.context import ContextProtocol
from app.domain.exceptions import NotFoundError, UnprocessableContentError
from app.domain.logger import logger
from app.domain.protocols import POSError
from app.domain.stores.entities import Store
from app.domain.stores.use_cases import get_stores
from app.domain.taxes.entities import Tax


class ArticleReferences(NamedTuple):
    category: Category
    tax: Tax
    stores: list[Store]


async def get_article_references(
    context: ContextProtocol,
    /,
    data: ArticleInput,
) -> ArticleReferences:
    category = await context.category_repository.get_by_name(name=data.category)
    if not category:
        raise NotFoundError(f"Category {data.category} not found")

    tax = await context.tax_repository.get_by_rate(rate=data.tax_rate)
    if not tax:
        raise NotFoundError(f"Tax {data.tax_rate} not found")

    stores = await get_stores(context)
    missing_stores = [store.name for store in stores if store.id not in data.prices]
    if missing_stores:
        raise UnprocessableContentError(
            f"Missing price for stores: {', '.join(missing_stores)}"
        )

    return ArticleReferences(
        category=category,
        tax=tax,
        stores=stores,
    )


async def create_pos_article(
    context: ContextProtocol,
    /,
    store: Store,
    category: Category,
    tax: Tax,
    name: str,
    price: Decimal,
    reference: str,
) -> POSAPIResult[RawArticle]:
    manager = await context.get_pos_manager(store)
    category_id = category.store_mapping[str(store.id)].id
    tax_id = tax.store_mapping[str(store.id)].id

    try:
        raw_article = await manager.create_article(
            category_id=category_id,
            tax_id=tax_id,
            name=name,
            price=price,
            reference=reference,
        )
    except POSError as error:
        logger.warning(f"Failed to create article in store {store.name}: {error}")
        return POSAPIResult(status=POSResultStatus.FAILED, data=None)

    return POSAPIResult(status=POSResultStatus.SUCCESS, data=raw_article)


async def update_pos_article(
    context: ContextProtocol,
    /,
    article_id: str,
    store: Store,
    category: Category,
    tax: Tax,
    name: str,
    price: Decimal,
    reference: str,
) -> POSAPIResult[RawArticle]:
    manager = await context.get_pos_manager(store)
    category_id = category.store_mapping[str(store.id)].id
    tax_id = tax.store_mapping[str(store.id)].id

    try:
        raw_article = await manager.update_article(
            article_id=article_id,
            category_id=category_id,
            tax_id=tax_id,
            name=name,
            price=price,
            reference=reference,
        )
    except POSError as error:
        logger.warning(f"Failed to update article in store {store.name}: {error}")
        return POSAPIResult(status=POSResultStatus.FAILED, data=None)

    return POSAPIResult(status=POSResultStatus.SUCCESS, data=raw_article)


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
