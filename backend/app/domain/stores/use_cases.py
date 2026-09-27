from app.domain.context import ContextProtocol
from app.domain.stores.entities import Store


async def get_stores(context: ContextProtocol) -> list[Store]:
    return await context.store_repository.get_all()
