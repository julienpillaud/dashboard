from typing import Annotated

from cleanstack import BaseEntity, EntityId
from pydantic import BaseModel, Field

from app.domain.articles.entities import ArticleDeposit
from app.domain.entities import DateTime, DecimalType


class InventorySummary(BaseModel):
    inventory_value: Annotated[DecimalType, Field(ge=0, decimal_places=2)]
    deposit_value: Annotated[DecimalType | None, Field(ge=0, decimal_places=2)]


class InventoryRecord(BaseModel):
    external_id: str
    name: str
    category: str
    stock_quantity: int
    total_cost: Annotated[DecimalType, Field(gt=0, decimal_places=4)]
    deposit: ArticleDeposit | None
    inventory_value: Annotated[DecimalType, Field(ge=0, decimal_places=2)]
    deposit_value: Annotated[DecimalType | None, Field(ge=0, decimal_places=2)]


class Inventory(BaseEntity):
    store_id: EntityId
    created_at: DateTime
    inventory_value: Annotated[DecimalType, Field(ge=0, decimal_places=2)]
    deposit_value: Annotated[DecimalType | None, Field(ge=0, decimal_places=2)]
    summary: dict[str, InventorySummary]
    records: list[InventoryRecord]
