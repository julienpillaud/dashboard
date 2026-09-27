from app.domain.context import ContextProtocol
from app.domain.origins.entities import Origin


async def get_origins(context: ContextProtocol) -> list[Origin]:
    return await context.origin_repository.get_all()
