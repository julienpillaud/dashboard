from cleanstack import BaseEntity
from pydantic import BaseModel

from app.domain.entities import BaseRawEntity


class RawCategory(BaseRawEntity):
    icon_text: str
    color: str


class CategoryFields(BaseModel):
    origin: bool
    color: bool
    taste: bool
    volume: bool
    alcohol_by_volume: bool
    deposit_unit: bool
    deposit_crate: bool
    deposit_packaging: bool


class Category(BaseEntity):
    name: str
    fields: CategoryFields
    store_mapping: dict[str, RawCategory]  # key is str(store.id)
