import uuid
from enum import StrEnum
from typing import Annotated

from cleanstack import BaseEntity, EntityId
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt, computed_field

from app.domain.entities import BaseRawEntity, DateTime, DecimalType
from app.domain.synchronization import SynchronizationItem


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

    def to_sync_item(self) -> SynchronizationItem:
        return SynchronizationItem(
            id=self.id,
            name=self.name,
            updated_at=self.updated_at,
            stock_quantity=self.stock_quantity,
        )


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
    store_name: str
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
