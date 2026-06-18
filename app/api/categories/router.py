from typing import Annotated

from cleanstack import PaginatedResponse
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_store, get_domain
from app.core.domain import Domain
from app.domain.categories.commands import (
    get_categories_command,
    get_raw_categories_command,
    synchronize_categories_command,
)
from app.domain.categories.entities import Category, RawCategory
from app.domain.stores.entities import Store

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("/raw", response_model=list[RawCategory])
async def get_raw_categories(
    current_store: Annotated[Store, Depends(get_current_store)],
    domain: Annotated[Domain, Depends(get_domain)],
    limit: int = 100,
    skip: int = 0,
) -> list[RawCategory]:
    return await domain.run(
        get_raw_categories_command,
        current_store,
        limit=limit,
        skip=skip,
    )


@router.get("", response_model=PaginatedResponse[Category])
async def get_categories(
    current_store: Annotated[Store, Depends(get_current_store)],
    domain: Annotated[Domain, Depends(get_domain)],
) -> PaginatedResponse[Category]:
    return await domain.run(get_categories_command, current_store)


@router.post("/synchronize")
async def synchronize_categories(
    current_store: Annotated[Store, Depends(get_current_store)],
    domain: Annotated[Domain, Depends(get_domain)],
) -> None:
    await domain.run(synchronize_categories_command, current_store)
