from collections.abc import Sequence
from typing import Protocol

from pydantic import BaseModel

from app.domain.entities import DateTime


class SyncableEntity(Protocol):
    def to_sync_item(self) -> SynchronizationItem: ...


class SynchronizationMetrics(BaseModel):
    pos_total: int
    db_before: int


class SynchronizationSummary(BaseModel):
    created: int
    updated: int
    deleted: int


class SynchronizationItem(BaseModel):
    id: str
    name: str
    updated_at: DateTime
    stock_quantity: int | None


class SynchronizationDetails(BaseModel):
    to_create: list[SynchronizationItem]
    to_update: list[SynchronizationItem]
    to_delete: list[SynchronizationItem]


class SynchronizationResponse(BaseModel):
    dry_run: bool
    store_slug: str
    metrics: SynchronizationMetrics
    summary: SynchronizationSummary
    details: SynchronizationDetails | None


def build_synchronization_response(
    dry_run: bool,
    store_slug: str,
    raw_items_count: int,
    items_count: int,
    to_create: Sequence[SyncableEntity],
    to_update: Sequence[SyncableEntity],
    to_delete: Sequence[SyncableEntity],
) -> SynchronizationResponse:
    details = (
        SynchronizationDetails(
            to_create=[item.to_sync_item() for item in to_create],
            to_update=[item.to_sync_item() for item in to_update],
            to_delete=[item.to_sync_item() for item in to_delete],
        )
        if dry_run
        else None
    )
    return SynchronizationResponse(
        dry_run=dry_run,
        store_slug=store_slug,
        metrics=SynchronizationMetrics(
            pos_total=raw_items_count,
            db_before=items_count,
        ),
        summary=SynchronizationSummary(
            created=len(to_create),
            updated=len(to_update),
            deleted=len(to_delete),
        ),
        details=details,
    )
