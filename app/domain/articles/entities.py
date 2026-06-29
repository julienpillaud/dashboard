import uuid
from enum import StrEnum
from typing import Annotated

from cleanstack import BaseEntity, EntityId
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt, computed_field

from app.domain.entities import BaseRawEntity, DateTime, DecimalType


class RawArticle(BaseRawEntity):
    category_id: str
    taxes: list[str]
    name: str
    icon_text: str
    color: str
    barcode: str | None
    in_stock: bool
    reference: str | None
    full_price: float | None
    stock_quantity: int | None


class VolumeUnit(StrEnum):
    CENTILITER = "cL"
    LITER = "L"


class ArticleVolume(BaseModel):
    value: PositiveFloat
    unit: VolumeUnit


class ArticleDeposit(BaseModel):
    unit: Annotated[DecimalType, Field(gt=0, decimal_places=2)]
    crate: Annotated[DecimalType, Field(gt=0, decimal_places=2)] | None
    packaging: PositiveInt | None


class ArticleOrigin(BaseModel):
    name: str
    code: str | None = None


class ArticleDetails(BaseModel):
    alcohol_by_volume: float | None
    volume: ArticleVolume | None
    origin: ArticleOrigin | None
    color: str | None
    taste: str | None
    distributor: str | None


class ArticleData(BaseModel):
    internal_id: uuid.UUID
    details: ArticleDetails | None
    total_cost: Annotated[DecimalType, Field(gt=0, decimal_places=4)]
    deposit: ArticleDeposit | None
    enhanced_at: DateTime


class ArticleStatus(StrEnum):
    DRAFT = "draft"
    OUTDATED = "outdated"
    SYNCED = "synced"


class Article(BaseEntity):
    store_id: EntityId
    category: str
    tax_rate: float
    raw: RawArticle
    data: ArticleData | None
    synced_at: DateTime

    @computed_field
    @property
    def status(self) -> ArticleStatus:
        if not self.data:
            return ArticleStatus.DRAFT

        if self.raw.updated_at > self.data.enhanced_at:
            return ArticleStatus.OUTDATED

        return ArticleStatus.SYNCED

    # @computed_field
    # @property
    # def inventory_value(self) -> float:
    #     if not (
    #         self.custom and self.raw.stock_quantity and self.raw.stock_quantity > 0
    #     ):
    #         return 0.0
    #
    #     value = self.custom.total_cost * Decimal(self.raw.stock_quantity)
    #     return float(value)
    #
    # @computed_field
    # @property
    # def deposit_value(self) -> float:
    #     if not (
    #         self.custom and self.raw.stock_quantity and self.raw.stock_quantity > 0
    #     ):
    #         return 0.0
    #
    #     if not self.custom.deposit:
    #         return 0.0
    #
    #     if self.custom.deposit.crate and self.custom.deposit.packaging:
    #         value = self.custom.deposit.crate * (
    #             Decimal(self.raw.stock_quantity)
    #             / Decimal(self.custom.deposit.packaging)
    #         )
    #         return float(value)
    #
    #     value = self.custom.deposit.unit * Decimal(self.raw.stock_quantity)
    #     return float(value)
