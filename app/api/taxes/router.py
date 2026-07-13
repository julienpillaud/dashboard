from typing import Annotated

from cleanstack import PaginatedResponse
from fastapi import APIRouter, Depends

from app.api.dependencies.app import DomainProvider
from app.api.dependencies.user import get_current_user
from app.core.domain import Domain
from app.domain.taxes.entities import Tax
from app.domain.taxes.use_cases import (
    get_taxes,
    synchronize_taxes,
)

router = APIRouter(
    prefix="/api/taxes",
    tags=["Taxes"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", summary="Get taxes")
async def get_taxes_endpoint(
    domain: Annotated[Domain, Depends(DomainProvider())],
    store: str | None = None,
) -> PaginatedResponse[Tax]:
    return await domain.run(get_taxes, store_slug=store)


@router.post("/synchronize", summary="Synchronize taxes")
async def synchronize_taxes_endpoint(
    domain: Annotated[Domain, Depends(DomainProvider())],
    store: str,
) -> None:
    await domain.run(synchronize_taxes, store_slug=store)
