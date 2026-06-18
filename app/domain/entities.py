import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel


def normalize_datetime(dt: datetime.datetime) -> datetime.datetime:
    # Ensure datetime returns by database is in UTC
    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.UTC)

    # MongoDB does not have enough precision to store microseconds
    return dt.replace(microsecond=(dt.microsecond // 1000) * 1000)


DateTime = Annotated[datetime.datetime, AfterValidator(normalize_datetime)]


class BaseRawEntity(BaseModel):
    id: str
    deprecated: bool
    created_at: DateTime
    updated_at: DateTime
