from cleanstack import BaseEntity, EntityId
from pydantic import BaseModel, EmailStr


class User(BaseEntity):
    email: EmailStr
    hashed_password: str


class UserExternal(BaseModel):
    id: EntityId
    email: EmailStr


class UserSession(BaseModel):
    access_token: str
    refresh_token: str
