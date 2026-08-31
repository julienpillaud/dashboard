from cleanstack import BaseEntity, EntityId

from app.domain.entities import BaseRawEntity
from app.domain.synchronization import SynchronizationItem


class RawTax(BaseRawEntity):
    name: str
    rate: float

    def to_sync_item(self) -> SynchronizationItem:
        return SynchronizationItem(
            id=self.id,
            name=self.name,
            updated_at=self.updated_at,
            stock_quantity=None,
        )


class Tax(BaseEntity):
    store_id: EntityId
    store_name: str
    raw: RawTax
