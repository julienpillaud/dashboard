from functools import cached_property

import httpx
from tactill import AsyncTactillClient

from app.core.domain import ResourceProtocol
from app.core.settings import Settings
from app.domain.articles.repository import ArticleRepositoryProtocol
from app.domain.categories.repository import CategoryRepositoryProtocol
from app.domain.context import ContextProtocol
from app.domain.inventories.repository import InventoryRepositoryProtocol
from app.domain.protocols import POSManagerProtocol
from app.domain.stores.entities import Store
from app.domain.stores.repository import StoreRepositoryProtocol
from app.domain.taxes.repository import TaxRepositoryProtocol
from app.domain.users.repository import UserRepositoryProtocol
from app.infrastructure.mongo.repositories.articles import ArticleRepository
from app.infrastructure.mongo.repositories.categories import CategoryRepository
from app.infrastructure.mongo.repositories.inventories import InventoryRepository
from app.infrastructure.mongo.repositories.stores import StoreRepository
from app.infrastructure.mongo.repositories.taxes import TaxRepository
from app.infrastructure.mongo.repositories.users import UserRepository
from app.infrastructure.mongo.resource.asynchronous import AsyncMongoResource
from app.infrastructure.tactill.manager import TactillManager


class Context(ContextProtocol):
    def __init__(
        self,
        settings: Settings,
        http_client: httpx.AsyncClient,
        resource: AsyncMongoResource,
    ) -> None:
        self.settings = settings
        self.http_client = http_client
        self.resource = resource
        self.database = self.resource.database
        self.session = self.resource.session

    @cached_property
    def user_repository(self) -> UserRepositoryProtocol:
        return UserRepository(database=self.database, session=self.session)

    @cached_property
    def store_repository(self) -> StoreRepositoryProtocol:
        return StoreRepository(database=self.database, session=self.session)

    @cached_property
    def tax_repository(self) -> TaxRepositoryProtocol:
        return TaxRepository(database=self.database, session=self.session)

    @cached_property
    def category_repository(self) -> CategoryRepositoryProtocol:
        return CategoryRepository(database=self.database, session=self.session)

    @cached_property
    def article_repository(self) -> ArticleRepositoryProtocol:
        return ArticleRepository(database=self.database, session=self.session)

    @cached_property
    def inventory_repository(self) -> InventoryRepositoryProtocol:
        return InventoryRepository(database=self.database, session=self.session)

    def get_pos_manager(self, store: Store) -> POSManagerProtocol:
        client = AsyncTactillClient(
            api_key=store.tactill_api_key,
            http_client=self.http_client,
        )
        return TactillManager(client=client)


class ContextProvider:
    def __init__(
        self,
        settings: Settings,
        http_client: httpx.AsyncClient,
    ) -> None:
        self._settings = settings
        self._http_client = http_client

    def __call__(self, resource: ResourceProtocol) -> Context:
        if not isinstance(resource, AsyncMongoResource):
            raise RuntimeError()

        return Context(
            settings=self._settings,
            http_client=self._http_client,
            resource=resource,
        )
