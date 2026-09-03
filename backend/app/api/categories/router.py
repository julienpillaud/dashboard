from typing import Annotated

from cleanstack import PaginatedResponse, Pagination
from fastapi import APIRouter, Depends

from app.api.dependencies.app import get_domain
from app.api.dependencies.user import get_current_user
from app.core.domain import Domain
from app.domain.categories.entities import Category
from app.domain.categories.use_cases import (
    get_categories,
    synchronize_categories,
)
from app.domain.synchronization.entities import SynchronizationResponse

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", summary="Get categories")
async def get_categories_endpoint(
    domain: Annotated[Domain, Depends(get_domain)],
    pagination: Annotated[Pagination, Depends()],
    store: str | None = None,
) -> PaginatedResponse[Category]:
    return await domain.run(get_categories, store_slug=store, pagination=pagination)


@router.post("/synchronize", summary="Synchronize categories")
async def synchronize_categories_endpoint(
    domain: Annotated[Domain, Depends(get_domain)],
    store: str,
    dry_run: bool = True,
) -> SynchronizationResponse:
    return await domain.run(synchronize_categories, store_slug=store, dry_run=dry_run)
