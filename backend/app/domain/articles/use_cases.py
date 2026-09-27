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
    POSCreationResult,
    POSStatus,
)
from app.domain.categories.entities import Category
from app.domain.context import ContextProtocol
from app.domain.exceptions import NotFoundError
from app.domain.protocols import (
    POSError,
)
from app.domain.stores.entities import Store
from app.domain.stores.use_cases import get_stores
from app.domain.taxes.entities import Tax


async def get_articles(
    context: ContextProtocol,
    /,
    filters: list[FilterEntity] | None = None,
    pagination: Pagination | None = None,
) -> PaginatedResponse[Article]:
    return await context.article_repository.get_all(
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
        article.add_store_result(store=store, price=data.price, result=result)

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
) -> POSCreationResult:
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
        return POSCreationResult(
            status=POSStatus.FAILED,
            raw=None,
            error=str(error),
        )

    return POSCreationResult(
        status=POSStatus.CREATED,
        raw=raw_article,
        error=None,
    )
