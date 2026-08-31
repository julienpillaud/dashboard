import uuid

from app.domain.categories.entities import Category, RawCategory
from app.domain.context import ContextProtocol
from app.domain.logger import logger
from app.domain.stores.entities import Store


async def create_category(
    context: ContextProtocol,
    /,
    store: Store,
    to_create: list[RawCategory],
) -> None:
    if not to_create:
        logger.info("Synchronization: No category to create")
        return

    categories = [
        Category(
            id=uuid.uuid7(),
            store_id=store.id,
            store_name=store.name,
            raw=category,
        )
        for category in to_create
    ]
    await context.category_repository.save_many(categories)


async def update_category(
    context: ContextProtocol,
    /,
    to_update: list[tuple[Category, RawCategory]],
) -> None:
    if not to_update:
        logger.info("Synchronization: No category to update")
        return

    categories = []
    for category, raw_category in to_update:
        category.raw = raw_category
        categories.append(category)

    await context.category_repository.update_many(categories)


async def delete_category(
    context: ContextProtocol,
    /,
    to_delete: list[Category],
) -> None:
    if not to_delete:
        logger.info("Synchronization: No category to delete")
        return

    await context.category_repository.delete_many(to_delete)
