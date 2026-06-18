from cleanstack import BaseEntity, EntityId
from pydantic import BaseModel


class Store(BaseEntity):
    name: str
    slug: str
    tactill_api_key: str
    hashed_password: str


class StorePublic(BaseModel):
    id: EntityId
    name: str
    slug: str
