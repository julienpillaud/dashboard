import datetime
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
    SYNCED = "synced"
    OUT_OF_SYNC = "out_of_sync"
    NOT_CREATED = "not_created"


class PosArticle(BaseModel):
    store_name: str
    price: Annotated[DecimalType, Field(gt=0, decimal_places=2)]
    status: POSStatus
    raw: RawArticle | None

    @classmethod
    def from_result(
        cls,
        store: Store,
        price: Decimal,
        result: POSAPIResult[RawArticle],
    ) -> PosArticle:
        status = (
            POSStatus.SYNCED
            if result.status == POSResultStatus.SUCCESS
            else POSStatus.NOT_CREATED
        )
        return cls(
            store_name=store.name,
            price=price,
            status=status,
            raw=result.data,
        )

    def apply_update(self, price: Decimal, result: POSAPIResult[RawArticle]) -> None:
        match result.status:
            case POSResultStatus.SUCCESS:
                self.status = POSStatus.SYNCED
                self.price = price
                self.raw = result.data
            case POSResultStatus.FAILED:
                self.status = POSStatus.OUT_OF_SYNC

    def synchronize(self, raw: RawArticle, /) -> None:
        self.raw = raw

    def needs_update(self, price: Decimal, has_pos_changes: bool) -> bool:
        # NOT_CREATED: nothing to update in the POS
        # OUT_OF_SYNC: the last update failed, retry even without changes
        # SYNCED: only if a field sent to the POS changed
        match self.status:
            case POSStatus.NOT_CREATED:
                return False
            case POSStatus.OUT_OF_SYNC:
                return True
            case POSStatus.SYNCED:
                return has_pos_changes or price != self.price


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

    def apply_input(self, data: ArticleInput, current_time: datetime.datetime) -> None:
        self.name = data.name
        self.category = data.category
        self.total_cost = data.total_cost
        self.tax_rate = data.tax_rate
        self.distributor = data.distributor
        self.details = data.details
        self.updated_at = current_time

    def add_store_mapping(
        self,
        store: Store,
        price: Decimal,
        result: POSAPIResult[RawArticle],
    ) -> None:
        self.store_mapping[str(store.id)] = PosArticle.from_result(
            store=store,
            price=price,
            result=result,
        )

    def update_store_mapping(
        self,
        store: Store,
        price: Decimal,
        result: POSAPIResult[RawArticle],
    ) -> None:
        self.store_mapping[str(store.id)].apply_update(price=price, result=result)

    def synchronize_store_mapping(self, raws: dict[str, RawArticle], /) -> None:
        for store_id, raw in raws.items():
            self.store_mapping[store_id].synchronize(raw)

    def has_pos_changes(self, data: ArticleInput, /) -> bool:
        # Fields sent to the POS: other fields only live in our database
        return (
            data.name != self.name
            or data.category != self.category
            or data.tax_rate != self.tax_rate
        )


class ArticleInput(BaseModel):
    name: str
    category: str
    total_cost: Annotated[DecimalType, Field(gt=0, decimal_places=4)]
    tax_rate: float
    distributor: str | None
    details: ArticleDetails
    prices: dict[EntityId, Annotated[DecimalType, Field(gt=0, decimal_places=2)]]


class POSResultStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"


class POSAPIResult[T](BaseModel):
    status: POSResultStatus
    data: T | None


class ArticleSynchronizationResult(BaseModel):
    updated: int
    failed_stores: list[str]
