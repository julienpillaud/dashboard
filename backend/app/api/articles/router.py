from typing import Annotated

from cleanstack import FilterEntity, PaginatedResponse, Pagination
from fastapi import APIRouter, Depends

from app.api.dependencies.app import get_domain
from app.api.dependencies.user import get_current_user
from app.api.filters import get_filters
from app.core.domain import Domain
from app.domain.articles.entities import Article
from app.domain.articles.use_cases import (
    get_articles,
    synchronize_articles,
)
from app.domain.synchronization import SynchronizationResponse

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
    store: str | None = None,
) -> PaginatedResponse[Article]:
    return await domain.run(
        get_articles,
        store_slug=store,
        filters=filters,
        pagination=pagination,
    )


@router.post("/synchronize", summary="Synchronize articles")
async def synchronize_articles_endpoint(
    domain: Annotated[Domain, Depends(get_domain)],
    store: str,
    dry_run: bool = True,
) -> SynchronizationResponse:
    return await domain.run(synchronize_articles, store_slug=store, dry_run=dry_run)
