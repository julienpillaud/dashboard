from decimal import Decimal
from enum import StrEnum
from typing import Annotated

from cleanstack import BaseEntity, EntityId
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt

from app.domain.entities import BaseRawEntity, DateTime, DecimalType
from app.domain.stores.entities import Store


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


class ArticleOrigin(BaseModel):
    name: str
    code: str | None = None


class ArticleDeposit(BaseModel):
    unit: Annotated[DecimalType, Field(gt=0, decimal_places=2)]
    crate: Annotated[DecimalType, Field(gt=0, decimal_places=2)] | None
    packaging: PositiveInt | None


class ArticleDetails(BaseModel):
    origin: ArticleOrigin | None
    color: str | None
    taste: str | None
    volume: ArticleVolume | None
    alcohol_by_volume: float | None
    deposit: ArticleDeposit | None


class POSStatus(StrEnum):
    CREATED = "created"
    FAILED = "failed"


class PosArticle(BaseModel):
    store_name: str
    price: Annotated[DecimalType, Field(gt=0, decimal_places=2)]
    status: POSStatus
    raw: RawArticle | None
    error: str | None


class Article(BaseEntity):
    name: str
    category: str
    total_cost: Annotated[DecimalType, Field(gt=0, decimal_places=4)]
    tax_rate: float
    distributor: str | None
    details: ArticleDetails
    store_mapping: dict[str, PosArticle] = Field(default_factory=dict)
    created_at: DateTime
    updated_at: DateTime

    def add_store_mapping(
        self,
        store: Store,
        price: Decimal,
        result: POSAPIResult[RawArticle],
    ) -> None:
        self.store_mapping[str(store.id)] = PosArticle(
            store_name=store.name,
            price=price,
            status=result.status,
            raw=result.data,
            error=result.error,
        )

    def update_store_mapping(self, raws: dict[str, RawArticle], /) -> None:
        for store_id, raw in raws.items():
            self.store_mapping[store_id].raw = raw


class ArticleCreate(BaseModel):
    name: str
    category: str
    total_cost: Annotated[DecimalType, Field(gt=0, decimal_places=4)]
    tax_rate: float
    distributor: str | None
    details: ArticleDetails
    prices: dict[EntityId, Annotated[DecimalType, Field(gt=0, decimal_places=2)]]


class POSAPIResult[T](BaseModel):
    status: POSStatus
    data: T | None
    error: str | None


class ArticleSynchronizationResult(BaseModel):
    updated: int
    failed_stores: list[str]
