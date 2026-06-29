import uuid

from app.domain.categories.entities import Category, RawCategory
from app.domain.context import ContextProtocol
from app.domain.stores.entities import Store


async def create_category(
    context: ContextProtocol,
    /,
    store: Store,
    to_create: list[RawCategory],
) -> None:
    categories = [
        Category(
            id=uuid.uuid7(),
            store_id=store.id,
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
    categories = []
    for category, raw_category in to_update:
        category.raw = raw_category
        categories.append(category)

    await context.category_repository.update_many(categories)
