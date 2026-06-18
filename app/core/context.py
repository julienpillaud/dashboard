from collections.abc import Callable
from functools import cached_property

import httpx
from cleanstack.mongo import MongoDocument
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase
from tactill import AsyncTactillClient

from app.core.settings import Settings
from app.domain.articles.repository import ArticleRepositoryProtocol
from app.domain.categories.repository import CategoryRepositoryProtocol
from app.domain.context import ContextProtocol
from app.domain.protocols import POSManagerProtocol
from app.domain.stores.repository import StoreRepositoryProtocol
from app.domain.taxes.repository import TaxRepositoryProtocol
from app.infrastructure.mongo.repositories.articles import ArticleRepository
from app.infrastructure.mongo.repositories.categories import CategoryRepository
from app.infrastructure.mongo.repositories.stores import StoreRepository
from app.infrastructure.mongo.repositories.taxes import TaxRepository
from app.infrastructure.tactill.manager import TactillManager

type ContextFactory = Callable[[AsyncClientSession | None], ContextProtocol]


class Context(ContextProtocol):
    def __init__(
        self,
        settings: Settings,
        http_client: httpx.AsyncClient,
        database: AsyncDatabase[MongoDocument],
        session: AsyncClientSession | None = None,
    ) -> None:
        self.settings = settings
        self.http_client = http_client
        self.database = database
        self.session = session

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
    def pos_manager(self) -> POSManagerProtocol:
        client = AsyncTactillClient(http_client=self.http_client)
        return TactillManager(client=client)
