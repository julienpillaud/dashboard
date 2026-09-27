from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies.app import get_domain
from app.core.domain import Domain
from app.domain.stores.entities import Store
from app.domain.stores.use_cases import get_stores

router = APIRouter(
    prefix="/stores",
    tags=["Stores"],
    # dependencies=[Depends(get_current_user)],
)


@router.get("", summary="Get stores")
async def get_stores_endpoint(
    domain: Annotated[Domain, Depends(get_domain)],
) -> list[Store]:
    return await domain.run(get_stores)
