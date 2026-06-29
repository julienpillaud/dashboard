from cleanstack import FilterEntity, PaginatedResponse

from app.domain.categories.entities import Category
from app.domain.categories.utils import create_category, update_category
from app.domain.context import ContextProtocol
from app.domain.exceptions import NotFoundError
from app.domain.logger import logger
from app.domain.stores.entities import Store


async def get_categories_command(
    context: ContextProtocol,
    /,
    store_slug: str | None = None,
) -> PaginatedResponse[Category]:
    filters = []
    if store_slug:
        store = await context.store_repository.get_by_slug(slug=store_slug)
        if not store:
            raise NotFoundError("Store not found")
        filters.append(FilterEntity(field="store_id", value=str(store.id)))

    return await context.category_repository.get_all(filters=filters)


async def get_category_command(
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


async def synchronize_categories_command(
    context: ContextProtocol,
    /,
    store_slug: str,
) -> None:
    store = await context.store_repository.get_by_slug(slug=store_slug)
    if not store:
        raise NotFoundError("Store not found")

    pos_manager = context.get_pos_manager(store=store)
    raw_categories = await pos_manager.get_categories()
    response = await context.category_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(store.id))],
    )
    categories_map = {category.raw.id: category for category in response.items}

    to_create = []
    to_update = []
    for raw_category in raw_categories:
        if raw_category.id not in categories_map:
            logger.info(f"Synchronization: Creating category: {raw_category.name}")
            to_create.append(raw_category)
        else:
            category = categories_map[raw_category.id]
            if category.raw.updated_at != raw_category.updated_at:
                logger.info(f"Synchronization: Updating category: {raw_category.name}")
                to_update.append((category, raw_category))

    await create_category(context, store, to_create=to_create)
    await update_category(context, to_update=to_update)
