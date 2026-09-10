import datetime
from decimal import Decimal
from typing import Annotated, Protocol

from pydantic import AfterValidator, BaseModel, PlainSerializer

DecimalType = Annotated[Decimal, PlainSerializer(float)]


def normalize_datetime(dt: datetime.datetime) -> datetime.datetime:
    # MongoDB does not have enough precision to store microseconds
    return dt.replace(
        microsecond=(dt.microsecond // 1000) * 1000,
        tzinfo=datetime.UTC,
    )


DateTime = Annotated[datetime.datetime, AfterValidator(normalize_datetime)]


class BaseRawEntity(BaseModel):
    id: str
    name: str
    deprecated: bool
    created_at: DateTime
    updated_at: DateTime


class DomainEntity(Protocol):
    @property
    def raw(self) -> BaseRawEntity: ...
