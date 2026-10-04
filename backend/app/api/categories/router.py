from fastapi import APIRouter, Depends

from app.api.dependencies.app import QueryDomain
from app.api.dependencies.user import get_current_user
from app.domain.categories.entities import Category
from app.domain.categories.use_cases import get_categories

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", summary="Get categories")
async def get_categories_endpoint(domain: QueryDomain) -> list[Category]:
    return await domain.run(get_categories)
