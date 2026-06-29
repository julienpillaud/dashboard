from app.domain.protocols import RepositoryProtocol
from app.domain.stores.entities import Store


class StoreRepositoryProtocol(RepositoryProtocol[Store]):
    async def get_by_slug(self, slug: str) -> Store | None: ...
