from typing import Annotated

from cleanstack import FilterEntity, PaginatedResponse, Pagination
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_domain
from app.api.filters import get_filters
from app.core.domain import Domain
from app.domain.articles.commands import (
    get_articles_command,
    synchronize_articles_command,
)
from app.domain.articles.entities import Article

router = APIRouter(
    prefix="/api/articles",
    tags=["Articles"],
    dependencies=[Depends(get_current_user)],
)


@router.get("")
async def get_articles(
    domain: Annotated[Domain, Depends(get_domain)],
    filters: Annotated[list[FilterEntity], Depends(get_filters)],
    pagination: Annotated[Pagination, Depends()],
    store: str | None = None,
) -> PaginatedResponse[Article]:
    return await domain.run(
        get_articles_command,
        store_slug=store,
        filters=filters,
        pagination=pagination,
    )


@router.post("/synchronize")
async def synchronize_articles(
    domain: Annotated[Domain, Depends(get_domain)],
    store: str,
) -> None:
    await domain.run(synchronize_articles_command, store_slug=store)
