from pydantic import BaseModel

from app.domain.categories.entities import Category, RawCategory
from app.domain.synchronization.entities import FieldChange


class CategoryUpdate(BaseModel):
    entity: Category
    raw_entity: RawCategory
    changes: list[FieldChange]


class CategorySynchronizationPlan(BaseModel):
    to_create: list[RawCategory]
    to_update: list[CategoryUpdate]
    to_delete: list[Category]
