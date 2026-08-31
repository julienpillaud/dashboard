from cleanstack import FilterEntity, PaginatedResponse, Pagination

from app.domain.categories.entities import Category
from app.domain.categories.utils import (
    create_category,
    delete_category,
    update_category,
)
from app.domain.context import ContextProtocol
from app.domain.exceptions import NotFoundError
from app.domain.logger import logger
from app.domain.stores.entities import Store
from app.domain.synchronization import (
    SynchronizationResponse,
    build_synchronization_response,
)


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
    raw_ids = {category.id for category in raw_categories}

    response = await context.category_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(store.id))],
    )
    categories_map = {category.raw.id: category for category in response.items}

    to_create = []
    to_update = []
    to_delete = []

    for raw_category in raw_categories:
        if raw_category.id not in categories_map:
            logger.info(f"Synchronization: Creating category: {raw_category.name}")
            to_create.append(raw_category)
        else:
            category = categories_map[raw_category.id]
            if category.raw.updated_at != raw_category.updated_at:
                logger.info(f"Synchronization: Updating category: {raw_category.name}")
                to_update.append((category, raw_category))

    for category_raw_id, category in categories_map.items():
        if category_raw_id not in raw_ids:
            logger.info(f"Synchronization: Deleting category: {category.raw.name}")
            to_delete.append(category)

    if not dry_run:
        await create_category(context, store, to_create=to_create)
        await update_category(context, to_update=to_update)
        await delete_category(context, to_delete=to_delete)

    return build_synchronization_response(
        dry_run=dry_run,
        store_slug=store_slug,
        raw_items_count=len(raw_categories),
        items_count=len(categories_map),
        to_create=to_create,
        to_update=[item for _, item in to_update],
        to_delete=[item.raw for item in to_delete],
    )
