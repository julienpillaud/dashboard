from app.domain.protocols import RepositoryProtocol
from app.domain.stores.entities import Store
from app.domain.taxes.entities import Tax


class TaxRepositoryProtocol(RepositoryProtocol[Tax]):
    async def get_by_external_id(
        self,
        current_store: Store,
        external_id: str,
    ) -> Tax | None: ...

    async def save_many(self, entities: list[Tax], /) -> None: ...

    async def update_many(self, entities: list[Tax], /) -> None: ...
