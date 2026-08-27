from app.domain.categories.entities import Category
from app.domain.protocols import RepositoryProtocol
from app.domain.stores.entities import Store


class CategoryRepositoryProtocol(RepositoryProtocol[Category]):
    async def get_by_external_id(
        self,
        current_store: Store,
        external_id: str,
    ) -> Category | None: ...

    async def save_many(self, entities: list[Category], /) -> None: ...

    async def update_many(self, entities: list[Category], /) -> None: ...
