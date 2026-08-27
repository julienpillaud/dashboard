from cleanstack import BaseEntity, EntityId

from app.domain.entities import BaseRawEntity


class RawCategory(BaseRawEntity):
    name: str
    icon_text: str
    color: str


class Category(BaseEntity):
    store_id: EntityId
    raw: RawCategory
