from typing import Annotated

from cleanstack import EntityId, FilterEntity, PaginatedResponse, Pagination
from fastapi import APIRouter, Depends, status

from app.api.dependencies.app import QueryDomain
from app.api.dependencies.user import get_current_user_id
from app.api.filters import get_filters
from app.api.search import get_search
from app.domain.articles.entities import (
    Article,
    ArticleInput,
    ArticleSynchronizationResult,
)
from app.domain.articles.use_cases import (
    create_article,
    get_articles,
    synchronize_articles,
    update_article,
)

router = APIRouter(
    prefix="/articles",
    tags=["Articles"],
    dependencies=[Depends(get_current_user_id)],
)


@router.get("", summary="Get articles")
async def get_articles_endpoint(
    domain: QueryDomain,
    search: Annotated[str | None, Depends(get_search)],
    filters: Annotated[list[FilterEntity], Depends(get_filters)],
    pagination: Annotated[Pagination, Depends()],
) -> PaginatedResponse[Article]:
    return await domain.run(
        get_articles,
        search=search,
        filters=filters,
        pagination=pagination,
    )


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create article")
async def create_article_endpoint(
    domain: QueryDomain,
    data: ArticleInput,
) -> Article:
    return await domain.run(create_article, data=data)


@router.put("/{article_id}", summary="Update article")
async def update_article_endpoint(
    domain: QueryDomain,
    article_id: EntityId,
    data: ArticleInput,
) -> Article:
    return await domain.run(update_article, article_id=article_id, data=data)


@router.post("/synchronize", summary="Synchronize articles")
async def synchronize_stocks_endpoint(
    domain: QueryDomain,
) -> ArticleSynchronizationResult:
    return await domain.run(synchronize_articles)
