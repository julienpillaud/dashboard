from enum import StrEnum
from typing import Annotated

from cleanstack import BaseEntity
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt

from app.domain.entities import BaseRawEntity, DateTime, DecimalType


class RawArticle(BaseRawEntity):
    category_id: str
    taxes: list[str]
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
    details: ArticleDetails | None
    total_cost: Annotated[DecimalType, Field(gt=0, decimal_places=4)]
    deposit: ArticleDeposit | None


class PosArticle(BaseModel):
    store_name: str
    price: float
    raw: RawArticle | None


class Article(BaseEntity):
    name: str
    category: str
    tax_rate: float
    data: ArticleData
    store_mapping: dict[str, PosArticle]
    created_at: DateTime
    updated_at: DateTime
