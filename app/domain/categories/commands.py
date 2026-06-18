import uuid

from cleanstack import FilterEntity, PaginatedResponse

from app.domain.categories.entities import Category, RawCategory
from app.domain.context import ContextProtocol
from app.domain.exceptions import NotFoundError
from app.domain.logger import logger
from app.domain.stores.entities import Store


async def get_raw_categories_command(
    context: ContextProtocol,
    /,
    current_store: Store,
    limit: int = 100,
    skip: int = 0,
) -> list[RawCategory]:
    return await context.pos_manager.get_categories(
        current_store,
        limit=limit,
        skip=skip,
    )


async def get_categories_command(
    context: ContextProtocol,
    /,
    current_store: Store,
) -> PaginatedResponse[Category]:
    return await context.category_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(current_store.id))],
    )


async def get_category_command(
    context: ContextProtocol,
    /,
    current_store: Store,
    external_id: str,
) -> Category:
    category = await context.category_repository.get_by_external_id(
        current_store,
        external_id=external_id,
    )
    if not category:
        raise NotFoundError("Category not found")

    return category


async def synchronize_categories_command(
    context: ContextProtocol,
    /,
    current_store: Store,
) -> None:
    raw_categories = await context.pos_manager.get_categories(current_store)
    raw_category_ids = {category.id for category in raw_categories}

    categories = await context.category_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(current_store.id))],
    )
    categories_map = {category.external_id: category for category in categories.items}

    for raw_category in raw_categories:
        if raw_category.id not in categories_map:
            logger.info(f"Synchronization: Creating category: {raw_category.name}")
            await create_category(context, current_store, raw_category=raw_category)
        else:
            raw_category_ids.discard(raw_category.id)
            category = categories_map[raw_category.id]
            if category.raw.updated_at != raw_category.updated_at:
                logger.info(f"Synchronization: Updating category: {raw_category.name}")
                await update_category(
                    context,
                    category=category,
                    raw_category=raw_category,
                )


async def create_category(
    context: ContextProtocol,
    /,
    current_store: Store,
    raw_category: RawCategory,
) -> Category:
    category = Category(
        id=uuid.uuid7(),
        store_id=current_store.id,
        external_id=raw_category.id,
        raw=raw_category,
    )
    await context.category_repository.save(category)
    return category


async def update_category(
    context: ContextProtocol,
    /,
    category: Category,
    raw_category: RawCategory,
) -> Category:
    category.raw = raw_category
    await context.category_repository.update(category)
    return category
