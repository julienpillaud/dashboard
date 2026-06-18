from typing import Annotated

from cleanstack import PaginatedResponse
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_store, get_domain
from app.core.domain import Domain
from app.domain.articles.commands import (
    get_articles_command,
    get_raw_articles_command,
    synchronize_articles_command,
)
from app.domain.articles.entities import Article, RawArticle
from app.domain.stores.entities import Store

router = APIRouter(prefix="/api/articles", tags=["Articles"])


@router.get("/raw", response_model=list[RawArticle])
async def get_raw_articles(
    current_store: Annotated[Store, Depends(get_current_store)],
    domain: Annotated[Domain, Depends(get_domain)],
    limit: int = 100,
    skip: int = 0,
) -> list[RawArticle]:
    return await domain.run(
        get_raw_articles_command,
        current_store,
        limit=limit,
        skip=skip,
    )


@router.get("", response_model=PaginatedResponse[Article])
async def get_articles(
    current_store: Annotated[Store, Depends(get_current_store)],
    domain: Annotated[Domain, Depends(get_domain)],
) -> PaginatedResponse[Article]:
    return await domain.run(get_articles_command, current_store)


@router.post("/synchronize")
async def synchronize_articles(
    current_store: Annotated[Store, Depends(get_current_store)],
    domain: Annotated[Domain, Depends(get_domain)],
) -> None:
    await domain.run(synchronize_articles_command, current_store)
