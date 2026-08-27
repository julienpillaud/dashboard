from typing import Protocol

from app.domain.articles.repository import ArticleRepositoryProtocol
from app.domain.categories.repository import CategoryRepositoryProtocol
from app.domain.inventories.repository import InventoryRepositoryProtocol
from app.domain.protocols import POSManagerProtocol
from app.domain.stores.entities import Store
from app.domain.stores.repository import StoreRepositoryProtocol
from app.domain.taxes.repository import TaxRepositoryProtocol
from app.domain.users.repository import UserRepositoryProtocol


class ContextProtocol(Protocol):
    @property
    def user_repository(self) -> UserRepositoryProtocol: ...

    @property
    def store_repository(self) -> StoreRepositoryProtocol: ...

    @property
    def tax_repository(self) -> TaxRepositoryProtocol: ...

    @property
    def category_repository(self) -> CategoryRepositoryProtocol: ...

    @property
    def article_repository(self) -> ArticleRepositoryProtocol: ...

    @property
    def inventory_repository(self) -> InventoryRepositoryProtocol: ...

    def get_pos_manager(self, store: Store) -> POSManagerProtocol: ...
