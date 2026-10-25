import uuid

from pydantic import BaseModel


class StorePublic(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
