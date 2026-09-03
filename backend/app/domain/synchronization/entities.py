from typing import Any

from pydantic import BaseModel

from app.domain.entities import DateTime


class FieldChange(BaseModel):
    field: str
    old_value: Any
    new_value: Any


class SynchronizationItem(BaseModel):
    id: str
    name: str
    created_at: DateTime
    updated_at: DateTime
    changes: list[FieldChange] = []


class SynchronizationDetails(BaseModel):
    to_create: list[SynchronizationItem]
    to_update: list[SynchronizationItem]
    to_delete: list[SynchronizationItem]


class SynchronizationMetrics(BaseModel):
    pos_total: int
    db_before: int


class SynchronizationSummary(BaseModel):
    created: int
    updated: int
    deleted: int


class SynchronizationResponse(BaseModel):
    dry_run: bool
    store_slug: str
    metrics: SynchronizationMetrics
    summary: SynchronizationSummary
    details: SynchronizationDetails | None
