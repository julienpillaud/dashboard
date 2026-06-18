from typing import Protocol

from app.domain.articles.repository import ArticleRepositoryProtocol
from app.domain.categories.repository import CategoryRepositoryProtocol
from app.domain.protocols import POSManagerProtocol
from app.domain.stores.repository import StoreRepositoryProtocol
from app.domain.taxes.repository import TaxRepositoryProtocol


class ContextProtocol(Protocol):
    @property
    def store_repository(self) -> StoreRepositoryProtocol: ...

    @property
    def tax_repository(self) -> TaxRepositoryProtocol: ...

    @property
    def category_repository(self) -> CategoryRepositoryProtocol: ...

    @property
    def article_repository(self) -> ArticleRepositoryProtocol: ...

    @property
    def pos_manager(self) -> POSManagerProtocol: ...
