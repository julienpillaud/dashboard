from cleanstack import BaseEntity, EntityId

from app.domain.entities import BaseRawEntity
from app.domain.synchronization import SynchronizationItem


class RawCategory(BaseRawEntity):
    name: str
    icon_text: str
    color: str

    def to_sync_item(self) -> SynchronizationItem:
        return SynchronizationItem(
            id=self.id,
            name=self.name,
            updated_at=self.updated_at,
            stock_quantity=None,
        )


class Category(BaseEntity):
    store_id: EntityId
    store_name: str
    raw: RawCategory
    is_visible: bool = True
