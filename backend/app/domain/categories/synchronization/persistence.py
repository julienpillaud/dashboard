import uuid

from app.domain.categories.entities import Category, RawCategory
from app.domain.categories.synchronization.entities import CategorySynchronizationPlan
from app.domain.context import ContextProtocol
from app.domain.logger import logger
from app.domain.stores.entities import Store


async def persist_synchronization_plan(
    context: ContextProtocol,
    /,
    store: Store,
    plan: CategorySynchronizationPlan,
) -> None:
    await create_categories(context, store=store, to_create=plan.to_create)
    await update_categories(
        context,
        to_update=[(item.entity, item.raw_entity) for item in plan.to_update],
    )
    await delete_categories(context, to_delete=plan.to_delete)


async def create_categories(
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


async def update_categories(
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


async def delete_categories(
    context: ContextProtocol,
    /,
    to_delete: list[Category],
) -> None:
    if not to_delete:
        logger.info("Synchronization: No category to delete")
        return

    await context.category_repository.delete_many(to_delete)
