from typing import Annotated

from cleanstack import PaginatedResponse
from fastapi import APIRouter, Depends

from app.api.dependencies.app import DomainProvider
from app.api.dependencies.user import get_current_user
from app.core.domain import Domain
from app.domain.categories.entities import Category
from app.domain.categories.use_cases import (
    get_categories,
    synchronize_categories,
)

router = APIRouter(
    prefix="/api/categories",
    tags=["Categories"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", summary="Get categories")
async def get_categories_endpoint(
    domain: Annotated[Domain, Depends(DomainProvider())],
    store: str | None = None,
) -> PaginatedResponse[Category]:
    return await domain.run(get_categories, store_slug=store)


@router.post("/synchronize", summary="Synchronize categories")
async def synchronize_categories_endpoint(
    domain: Annotated[Domain, Depends(DomainProvider())],
    store: str,
) -> None:
    await domain.run(synchronize_categories, store_slug=store)
