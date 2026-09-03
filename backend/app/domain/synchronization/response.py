from app.domain.entities import BaseRawEntity
from app.domain.synchronization.entities import (
    FieldChange,
    SynchronizationDetails,
    SynchronizationItem,
    SynchronizationMetrics,
    SynchronizationResponse,
    SynchronizationSummary,
)
from app.domain.synchronization.protocols import SynchronizationPlanProtocol


def build_synchronization_item(
    entity: BaseRawEntity,
    changes: list[FieldChange] | None = None,
) -> SynchronizationItem:
    return SynchronizationItem(
        id=entity.id,
        name=entity.name,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        changes=changes or [],
    )


def build_synchronization_response(
    dry_run: bool,
    store_slug: str,
    raw_items_count: int,
    items_count: int,
    plan: SynchronizationPlanProtocol,
) -> SynchronizationResponse:
    to_create = [build_synchronization_item(item) for item in plan.to_create]
    to_update = [
        build_synchronization_item(item.raw_entity, item.changes)
        for item in plan.to_update
    ]
    to_delete = [build_synchronization_item(item.raw) for item in plan.to_delete]

    return SynchronizationResponse(
        dry_run=dry_run,
        store_slug=store_slug,
        metrics=SynchronizationMetrics(
            pos_total=raw_items_count,
            db_before=items_count,
        ),
        summary=SynchronizationSummary(
            created=len(plan.to_create),
            updated=len(plan.to_update),
            deleted=len(plan.to_delete),
        ),
        details=SynchronizationDetails(
            to_create=to_create,
            to_update=to_update,
            to_delete=to_delete,
        )
        if dry_run
        else None,
    )
