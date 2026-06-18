from typing import Annotated

from cleanstack import PaginatedResponse
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_store, get_domain
from app.core.domain import Domain
from app.domain.stores.entities import Store
from app.domain.taxes.commands import (
    get_raw_taxes_command,
    get_taxes_command,
    synchronize_taxes_command,
)
from app.domain.taxes.entities import RawTax, Tax

router = APIRouter(prefix="/api/taxes", tags=["Taxes"])


@router.get("/raw", response_model=list[RawTax])
async def get_raw_taxes(
    current_store: Annotated[Store, Depends(get_current_store)],
    domain: Annotated[Domain, Depends(get_domain)],
    limit: int = 100,
    skip: int = 0,
) -> list[RawTax]:
    return await domain.run(
        get_raw_taxes_command,
        current_store,
        limit=limit,
        skip=skip,
    )


@router.get("", response_model=PaginatedResponse[Tax])
async def get_taxes(
    current_store: Annotated[Store, Depends(get_current_store)],
    domain: Annotated[Domain, Depends(get_domain)],
) -> PaginatedResponse[Tax]:
    return await domain.run(get_taxes_command, current_store)


@router.post("/synchronize")
async def synchronize_taxes(
    current_store: Annotated[Store, Depends(get_current_store)],
    domain: Annotated[Domain, Depends(get_domain)],
) -> None:
    await domain.run(synchronize_taxes_command, current_store)
