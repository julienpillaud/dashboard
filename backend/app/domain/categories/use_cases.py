from cleanstack import SortEntity, SortOrder

from app.domain.categories.entities import Category
from app.domain.context import ContextProtocol


async def get_categories(context: ContextProtocol, /) -> list[Category]:
    return await context.category_repository.get_all(
        sort=[SortEntity(field="name", order=SortOrder.ASC)],
    )
