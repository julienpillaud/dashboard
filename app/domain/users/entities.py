from cleanstack import BaseEntity, EntityId
from pydantic import BaseModel


class User(BaseEntity):
    name: str
    hashed_password: str


class UserExternal(BaseModel):
    id: EntityId
    name: str
