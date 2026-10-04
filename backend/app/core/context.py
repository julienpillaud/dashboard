from functools import cached_property

from app.core.protocols import UnitOfWorkProtocol
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
from app.infrastructure.mongo.uow import MongoUnitOfWork
from app.infrastructure.tactill.factory import TactillClientFactory
from app.infrastructure.tactill.manager import TactillManager


class Context(ContextProtocol):
    def __init__(
        self,
        uow: MongoUnitOfWork,
        tactill_factory: TactillClientFactory,
    ) -> None:
        self.resource = uow.resource
        self.database = uow.resource.database
        self.session = uow.session
        self.tactill_factory = tactill_factory

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
    def __init__(self, tactill_factory: TactillClientFactory) -> None:
        self.tactill_factory = tactill_factory

    def __call__(self, uow: UnitOfWorkProtocol) -> Context:
        if not isinstance(uow, MongoUnitOfWork):
            raise RuntimeError()

        return Context(uow=uow, tactill_factory=self.tactill_factory)
