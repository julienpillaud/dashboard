from app.domain.context import ContextProtocol
from app.domain.exceptions import NotFoundError
from app.domain.pricing.entities import (
    RecommendedPriceRequest,
    RecommendedPriceResponse,
)


async def compute_recommended_price(
    context: ContextProtocol,
    data: RecommendedPriceRequest,
) -> RecommendedPriceResponse:
    pricing_rules = await context.pricing_rules_repository.get_by_store_and_category(
        store_id=data.store_id,
        category_id=data.category_id,
    )
    if not pricing_rules:
        raise NotFoundError("Pricing rules not found")

    pricing_config = pricing_rules.pricing_config
    value = pricing_config.value
    if (
        pricing_config.adjustment
        and data.total_cost >= pricing_config.adjustment.threshold
    ):
        value += pricing_config.adjustment.extra_value

    tax_factor = 1 + (data.tax_rate / 100)
    match pricing_config.operator:
        case "+":
            price = (data.total_cost + value) * tax_factor
        case "*":
            price = (data.total_cost * value) * tax_factor

    round_config = pricing_config.round_config
    quotient = (price / round_config.value).to_integral_value(
        rounding=str(round_config.round_mode)
    )
    recommended_price = quotient * round_config.value
    return RecommendedPriceResponse(recommended_price=recommended_price)
