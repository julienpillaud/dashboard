from cleanstack import BaseEntity, EntityId

from app.domain.entities import BaseRawEntity


class RawCategory(BaseRawEntity):
    icon_text: str
    color: str


class Category(BaseEntity):
    store_id: EntityId
    store_name: str
    raw: RawCategory
    is_visible: bool = True
