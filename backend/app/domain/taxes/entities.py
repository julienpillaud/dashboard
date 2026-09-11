from cleanstack import BaseEntity

from app.domain.entities import BaseRawEntity


class RawTax(BaseRawEntity):
    rate: float


class Tax(BaseEntity):
    rate: float
    store_mapping: dict[str, RawTax]
