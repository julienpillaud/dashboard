from fastapi import APIRouter, Depends

from app.api.dependencies.app import QueryDomain
from app.api.dependencies.user import get_current_user
from app.domain.pricing.entities import (
    RecommendedPriceRequest,
    RecommendedPriceResponse,
)
from app.domain.pricing.use_cases import compute_recommended_price

router = APIRouter(
    prefix="/pricing",
    tags=["Pricing"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/recommended-price")
async def recommended_price_endpoint(
    domain: QueryDomain,
    data: RecommendedPriceRequest,
) -> RecommendedPriceResponse:
    return await domain.run(compute_recommended_price, data=data)
