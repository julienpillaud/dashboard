from cleanstack import BaseEntity, EntityId

from app.domain.entities import BaseRawEntity


class RawTax(BaseRawEntity):
    name: str
    rate: float


class Tax(BaseEntity):
    store_id: EntityId
    external_id: str
    raw: RawTax
