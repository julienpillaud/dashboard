from cleanstack import FilterEntity, PaginatedResponse

from app.domain.context import ContextProtocol
from app.domain.exceptions import NotFoundError
from app.domain.stores.entities import Store
from app.domain.synchronization.entities import SynchronizationResponse
from app.domain.synchronization.response import build_synchronization_response
from app.domain.taxes.entities import Tax
from app.domain.taxes.synchronisation.persistence import persist_synchronization_plan
from app.domain.taxes.synchronisation.plan import build_synchronization_plan


async def get_taxes(
    context: ContextProtocol,
    /,
    store_slug: str | None = None,
) -> PaginatedResponse[Tax]:
    filters = []
    if store_slug:
        store = await context.store_repository.get_by_slug(slug=store_slug)
        if not store:
            raise NotFoundError("Store not found")
        filters.append(FilterEntity(field="store_id", value=str(store.id)))

    return await context.tax_repository.get_all(filters=filters)


async def get_tax_by_external_id(
    context: ContextProtocol,
    /,
    store: Store,
    external_id: str,
) -> Tax:
    tax = await context.tax_repository.get_by_external_id(
        store,
        external_id=external_id,
    )
    if not tax:
        raise NotFoundError("Tax not found")

    return tax


async def synchronize_taxes(
    context: ContextProtocol,
    /,
    store_slug: str,
    dry_run: bool = True,
) -> SynchronizationResponse:
    store = await context.store_repository.get_by_slug(slug=store_slug)
    if not store:
        raise NotFoundError("Store not found")

    pos_manager = context.get_pos_manager(store=store)
    raw_taxes = await pos_manager.get_taxes()

    response = await context.tax_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(store.id))],
    )

    plan = build_synchronization_plan(
        raw_taxes=raw_taxes,
        taxes=response.items,
    )
    if not dry_run:
        await persist_synchronization_plan(context, store=store, plan=plan)

    return build_synchronization_response(
        dry_run=dry_run,
        store_slug=store_slug,
        raw_items_count=len(raw_taxes),
        items_count=len(response.items),
        plan=plan,
    )
