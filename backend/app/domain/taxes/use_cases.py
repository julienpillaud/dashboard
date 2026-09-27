from cleanstack import SortEntity, SortOrder

from app.domain.context import ContextProtocol
from app.domain.taxes.entities import Tax


async def get_taxes(context: ContextProtocol, /) -> list[Tax]:
    return await context.tax_repository.get_all(
        sort=[SortEntity(field="rate", order=SortOrder.ASC)],
    )
