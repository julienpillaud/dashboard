from cleanstack import PaginatedResponse

from app.domain.context import ContextProtocol
from app.domain.taxes.entities import Tax


async def get_taxes(context: ContextProtocol, /) -> PaginatedResponse[Tax]:
    return await context.tax_repository.get_all()
