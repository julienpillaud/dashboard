from typing import Annotated

from cleanstack import FilterEntity, PaginatedResponse, Pagination
from fastapi import APIRouter, Depends, status

from app.api.dependencies.app import get_domain
from app.api.filters import get_filters
from app.api.search import get_search
from app.core.domain import Domain
from app.domain.articles.entities import Article, ArticleCreate
from app.domain.articles.use_cases import create_article, get_articles

router = APIRouter(
    prefix="/articles",
    tags=["Articles"],
    # dependencies=[Depends(get_current_user)],
)


@router.get("", summary="Get articles")
async def get_articles_endpoint(
    domain: Annotated[Domain, Depends(get_domain)],
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
    domain: Annotated[Domain, Depends(get_domain)],
    data: ArticleCreate,
) -> Article:
    return await domain.run(create_article, data=data)
