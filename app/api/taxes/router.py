from typing import Annotated

from cleanstack import PaginatedResponse
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_domain
from app.core.domain import Domain
from app.domain.taxes.commands import (
    get_taxes_command,
    synchronize_taxes_command,
)
from app.domain.taxes.entities import Tax

router = APIRouter(
    prefix="/api/taxes",
    tags=["Taxes"],
    dependencies=[Depends(get_current_user)],
)


@router.get("")
async def get_taxes(
    domain: Annotated[Domain, Depends(get_domain)],
    store: str | None = None,
) -> PaginatedResponse[Tax]:
    return await domain.run(get_taxes_command, store_slug=store)


@router.post("/synchronize")
async def synchronize_taxes(
    domain: Annotated[Domain, Depends(get_domain)],
    store: str,
) -> None:
    await domain.run(synchronize_taxes_command, store_slug=store)
