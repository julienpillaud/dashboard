from app.domain.categories.entities import Category, RawCategory
from app.domain.categories.synchronization.entities import (
    CategorySynchronizationPlan,
    CategoryUpdate,
)
from app.domain.logger import logger
from app.domain.synchronization.utils import compute_changes


def build_synchronization_plan(
    raw_categories: list[RawCategory],
    categories: list[Category],
) -> CategorySynchronizationPlan:
    to_create: list[RawCategory] = []
    to_update: list[CategoryUpdate] = []
    to_delete: list[Category] = []

    categories_map = {category.raw.id: category for category in categories}
    for raw_category in raw_categories:
        category = categories_map.get(raw_category.id)

        if category is None:
            logger.info(f"Synchronization: Creating category: {raw_category.name}")
            to_create.append(raw_category)
            continue

        if category.raw.updated_at != raw_category.updated_at:
            logger.info(f"Synchronization: Updating category: {raw_category.name}")
            changes = compute_changes(old=category.raw, new=raw_category)
            to_update.append(
                CategoryUpdate(
                    entity=category,
                    raw_entity=raw_category,
                    changes=changes,
                )
            )

    raw_ids = {category.id for category in raw_categories}
    for category_raw_id, category in categories_map.items():
        if category_raw_id not in raw_ids:
            logger.info(f"Synchronization: Deleting category: {category.raw.name}")
            to_delete.append(category)

    return CategorySynchronizationPlan(
        to_create=to_create,
        to_update=to_update,
        to_delete=to_delete,
    )
