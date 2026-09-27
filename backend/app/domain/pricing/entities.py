from decimal import ROUND_CEILING, ROUND_HALF_EVEN
from enum import Enum
from typing import Annotated, Literal

from cleanstack import BaseEntity, EntityId
from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import DecimalType


class RoundMode(Enum):
    ROUND_HALF_EVEN = ROUND_HALF_EVEN
    ROUND_CEILING = ROUND_CEILING


class RoundConfig(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    value: DecimalType
    round_mode: RoundMode


class ThresholdAdjustment(BaseModel):
    threshold: DecimalType
    extra_value: DecimalType


class PricingConfig(BaseModel):
    value: DecimalType
    operator: Literal["+", "*"]
    round_config: RoundConfig
    adjustment: ThresholdAdjustment | None


class PricingRule(BaseEntity):
    store_id: EntityId
    category_id: EntityId
    pricing_config: PricingConfig


class RecommendedPriceRequest(BaseModel):
    store_id: EntityId
    category_id: EntityId
    total_cost: Annotated[DecimalType, Field(gt=0, decimal_places=4)]
    tax_rate: DecimalType


class RecommendedPriceResponse(BaseModel):
    recommended_price: DecimalType
