from functools import cached_property

import httpx2

from app.core.domain import TransactionProtocol
from app.core.settings import Settings
from app.domain.articles.repository import ArticleRepositoryProtocol
from app.domain.categories.repository import CategoryRepositoryProtocol
from app.domain.context import ContextProtocol
from app.domain.inventories.repository import InventoryRepositoryProtocol
from app.domain.origins.repository import OriginRepositoryProtocol
from app.domain.pricing.repository import PricingRuleRepositoryProtocol
from app.domain.protocols import POSManagerProtocol
from app.domain.refresh_tokens.repository import RefreshTokenRepositoryProtocol
from app.domain.stores.entities import Store
from app.domain.stores.repository import StoreRepositoryProtocol
from app.domain.taxes.repository import TaxRepositoryProtocol
from app.domain.users.repository import UserRepositoryProtocol
from app.infrastructure.mongo.repositories.articles import ArticleRepository
from app.infrastructure.mongo.repositories.categories import CategoryRepository
from app.infrastructure.mongo.repositories.inventories import InventoryRepository
from app.infrastructure.mongo.repositories.origins import OriginRepository
from app.infrastructure.mongo.repositories.pricing_rules import PricingRuleRepository
from app.infrastructure.mongo.repositories.refresh_tokens import RefreshTokenRepository
from app.infrastructure.mongo.repositories.stores import StoreRepository
from app.infrastructure.mongo.repositories.taxes import TaxRepository
from app.infrastructure.mongo.repositories.users import UserRepository
from app.infrastructure.mongo.resource.asynchronous import MongoTransaction
from app.infrastructure.tactill.factory import TactillClientFactory
from app.infrastructure.tactill.manager import TactillManager


class Context(ContextProtocol):
    def __init__(
        self,
        settings: Settings,
        http_client: httpx2.AsyncClient,
        tactill_factory: TactillClientFactory,
        transaction: MongoTransaction,
    ) -> None:
        self.settings = settings
        self.http_client = http_client
        self.tactill_factory = tactill_factory
        self.transaction = transaction
        self.database = transaction.resource.database
        self.session = transaction.session

    @cached_property
    def user_repository(self) -> UserRepositoryProtocol:
        return UserRepository(database=self.database, session=self.session)

    @cached_property
    def refresh_token_repository(self) -> RefreshTokenRepositoryProtocol:
        return RefreshTokenRepository(database=self.database, session=self.session)

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
    def pricing_rules_repository(self) -> PricingRuleRepositoryProtocol:
        return PricingRuleRepository(database=self.database, session=self.session)

    @cached_property
    def origin_repository(self) -> OriginRepositoryProtocol:
        return OriginRepository(database=self.database, session=self.session)

    @cached_property
    def article_repository(self) -> ArticleRepositoryProtocol:
        return ArticleRepository(database=self.database, session=self.session)

    @cached_property
    def inventory_repository(self) -> InventoryRepositoryProtocol:
        return InventoryRepository(database=self.database, session=self.session)

    async def get_pos_manager(self, store: Store) -> POSManagerProtocol:
        client = await self.tactill_factory.get(store.pos_api_key)
        return TactillManager(client=client)


class ContextProvider:
    def __init__(
        self,
        settings: Settings,
        http_client: httpx2.AsyncClient,
        tactill_factory: TactillClientFactory,
    ) -> None:
        self._settings = settings
        self._http_client = http_client
        self._tactill_factory = tactill_factory

    def __call__(self, transaction: TransactionProtocol) -> Context:
        if not isinstance(transaction, MongoTransaction):
            raise RuntimeError()

        return Context(
            settings=self._settings,
            http_client=self._http_client,
            tactill_factory=self._tactill_factory,
            transaction=transaction,
        )
