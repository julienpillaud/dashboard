from typing import Annotated

from cleanstack import PaginatedResponse, Pagination
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_domain
from app.core.domain import Domain
from app.domain.inventories.commands import (
    create_inventory_command,
    get_inventories_command,
)
from app.domain.inventories.entities import Inventory

router = APIRouter(
    prefix="/api/inventories",
    tags=["Inventories"],
    dependencies=[Depends(get_current_user)],
)


@router.get("")
async def get_inventories(
    domain: Annotated[Domain, Depends(get_domain)],
    pagination: Annotated[Pagination, Depends()],
    store_slug: str,
) -> PaginatedResponse[Inventory]:
    return await domain.run(
        get_inventories_command,
        pagination=pagination,
        store_slug=store_slug,
    )


@router.post("")
async def create_inventory(
    domain: Annotated[Domain, Depends(get_domain)],
    store: str,
) -> Inventory:
    return await domain.run(create_inventory_command, store_slug=store)
