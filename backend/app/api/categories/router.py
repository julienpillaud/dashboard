from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies.app import get_domain
from app.core.domain import Domain
from app.domain.categories.entities import Category
from app.domain.categories.use_cases import get_categories

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    # dependencies=[Depends(get_current_user)],
)


@router.get("", summary="Get categories")
async def get_categories_endpoint(
    domain: Annotated[Domain, Depends(get_domain)],
) -> list[Category]:
    return await domain.run(get_categories)
