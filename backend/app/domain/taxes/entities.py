from cleanstack import BaseEntity, EntityId

from app.domain.entities import BaseRawEntity


class RawTax(BaseRawEntity):
    rate: float


class Tax(BaseEntity):
    store_id: EntityId
    store_name: str
    raw: RawTax
