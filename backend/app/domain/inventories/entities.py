from typing import Annotated

from cleanstack import BaseEntity, EntityId
from pydantic import BaseModel, Field

from app.domain.articles.entities import ArticleDeposit
from app.domain.entities import DateTime, DecimalType


class InventoryAmounts(BaseModel):
    amount: Annotated[DecimalType, Field(ge=0, decimal_places=4)]
    deposit_amount: Annotated[DecimalType, Field(ge=0, decimal_places=4)]

    @property
    def total_amount(self) -> DecimalType:
        return self.amount + self.deposit_amount


class InventoryRecord(BaseModel):
    external_id: str
    name: str
    category: str
    tax_rate: float
    stock_quantity: int
    total_cost: Annotated[DecimalType, Field(gt=0, decimal_places=4)]
    deposit: ArticleDeposit | None
    amounts: InventoryAmounts


class Inventory(BaseEntity):
    store_id: EntityId
    store_name: str
    created_at: DateTime
    amounts: InventoryAmounts
    articles_count: int
    category_summary: dict[str, InventoryAmounts]
    tax_summary: dict[str, InventoryAmounts]
    records: list[InventoryRecord]
