from cleanstack import PaginatedResponse

from app.domain.categories.entities import Category
from app.domain.context import ContextProtocol


async def get_categories(context: ContextProtocol, /) -> PaginatedResponse[Category]:
    return await context.category_repository.get_all()
