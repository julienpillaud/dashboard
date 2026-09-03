from cleanstack import FilterEntity, PaginatedResponse, Pagination

from app.domain.categories.entities import Category
from app.domain.categories.synchronization.persistence import (
    persist_synchronization_plan,
)
from app.domain.categories.synchronization.plan import build_synchronization_plan
from app.domain.context import ContextProtocol
from app.domain.exceptions import NotFoundError
from app.domain.stores.entities import Store
from app.domain.synchronization.entities import SynchronizationResponse
from app.domain.synchronization.response import build_synchronization_response


async def get_categories(
    context: ContextProtocol,
    /,
    store_slug: str | None = None,
    pagination: Pagination | None = None,
) -> PaginatedResponse[Category]:
    filters = []
    if store_slug:
        store = await context.store_repository.get_by_slug(slug=store_slug)
        if not store:
            raise NotFoundError("Store not found")
        filters.append(FilterEntity(field="store_id", value=str(store.id)))

    return await context.category_repository.get_all(
        filters=filters,
        pagination=pagination,
    )


async def get_category_by_external_id(
    context: ContextProtocol,
    /,
    store: Store,
    external_id: str,
) -> Category:
    category = await context.category_repository.get_by_external_id(
        store,
        external_id=external_id,
    )
    if not category:
        raise NotFoundError("Category not found")

    return category


async def synchronize_categories(
    context: ContextProtocol,
    /,
    store_slug: str,
    dry_run: bool = True,
) -> SynchronizationResponse:
    store = await context.store_repository.get_by_slug(slug=store_slug)
    if not store:
        raise NotFoundError("Store not found")

    pos_manager = context.get_pos_manager(store=store)
    raw_categories = await pos_manager.get_categories()

    response = await context.category_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(store.id))],
    )

    plan = build_synchronization_plan(
        raw_categories=raw_categories,
        categories=response.items,
    )

    if not dry_run:
        await persist_synchronization_plan(context, store=store, plan=plan)

    return build_synchronization_response(
        dry_run=dry_run,
        store_slug=store_slug,
        raw_items_count=len(raw_categories),
        items_count=len(response.items),
        plan=plan,
    )
