from fastapi import APIRouter, Depends

from app.api.dependencies.app import QueryDomain
from app.api.dependencies.user import get_current_user_id
from app.api.stores.dtos import StorePublic
from app.domain.stores.entities import Store
from app.domain.stores.use_cases import get_stores

router = APIRouter(
    prefix="/stores",
    tags=["Stores"],
    dependencies=[Depends(get_current_user_id)],
)


@router.get("", response_model=list[StorePublic], summary="Get stores")
async def get_stores_endpoint(domain: QueryDomain) -> list[Store]:
    return await domain.run(get_stores)
