from typing import Annotated

from cleanstack import PaginatedResponse
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_domain
from app.core.domain import Domain
from app.domain.categories.commands import (
    get_categories_command,
    synchronize_categories_command,
)
from app.domain.categories.entities import Category

router = APIRouter(
    prefix="/api/categories",
    tags=["Categories"],
    dependencies=[Depends(get_current_user)],
)


@router.get("")
async def get_categories(
    domain: Annotated[Domain, Depends(get_domain)],
    store: str | None = None,
) -> PaginatedResponse[Category]:
    return await domain.run(get_categories_command, store_slug=store)


@router.post("/synchronize")
async def synchronize_categories(
    domain: Annotated[Domain, Depends(get_domain)],
    store: str,
) -> None:
    await domain.run(synchronize_categories_command, store_slug=store)
