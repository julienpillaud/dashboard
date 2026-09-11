from typing import Annotated

from cleanstack import FilterEntity, PaginatedResponse, Pagination
from fastapi import APIRouter, Depends

from app.api.dependencies.app import get_domain
from app.api.dependencies.user import get_current_user
from app.api.filters import get_filters
from app.core.domain import Domain
from app.domain.articles.entities import Article
from app.domain.articles.use_cases import get_articles

router = APIRouter(
    prefix="/articles",
    tags=["Articles"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", summary="Get articles")
async def get_articles_endpoint(
    domain: Annotated[Domain, Depends(get_domain)],
    filters: Annotated[list[FilterEntity], Depends(get_filters)],
    pagination: Annotated[Pagination, Depends()],
) -> PaginatedResponse[Article]:
    return await domain.run(get_articles, filters=filters, pagination=pagination)
