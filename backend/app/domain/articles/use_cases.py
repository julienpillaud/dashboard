from cleanstack import (
    FilterEntity,
    PaginatedResponse,
    Pagination,
    SortEntity,
    SortOrder,
)

from app.domain.articles.entities import Article
from app.domain.context import ContextProtocol


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
