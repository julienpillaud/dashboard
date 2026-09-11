from cleanstack import BaseEntity

from app.domain.entities import BaseRawEntity


class RawCategory(BaseRawEntity):
    icon_text: str
    color: str


class Category(BaseEntity):
    name: str
    store_mapping: dict[str, RawCategory]
