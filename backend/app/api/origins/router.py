from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies.app import get_domain
from app.core.domain import Domain
from app.domain.origins.entities import Origin
from app.domain.origins.use_cases import get_origins

router = APIRouter(
    prefix="/origins",
    tags=["Origins"],
    # dependencies=[Depends(get_current_user)],
)


@router.get("", summary="Get origins")
async def get_origins_endpoint(
    domain: Annotated[Domain, Depends(get_domain)],
) -> list[Origin]:
    return await domain.run(get_origins)
