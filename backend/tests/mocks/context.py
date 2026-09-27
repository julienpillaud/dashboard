import httpx2

from app.core.context import Context
from app.core.domain import TransactionProtocol
from app.core.settings import Settings
from app.domain.protocols import POSManagerProtocol
from app.domain.stores.entities import Store
from app.infrastructure.mongo.resource.asynchronous import MongoTransaction
from app.infrastructure.tactill.factory import TactillClientFactory
from tests.mocks.pos_manager import FakePOSManager


class MockContext(Context):
    def __init__(
        self,
        settings: Settings,
        http_client: httpx2.AsyncClient,
        transaction: MongoTransaction,
        pos_manager: FakePOSManager,
    ) -> None:
        super().__init__(
            settings=settings,
            http_client=http_client,
            tactill_factory=TactillClientFactory(http_client),
            transaction=transaction,
        )
        self._pos_manager = pos_manager

    async def get_pos_manager(self, store: Store) -> POSManagerProtocol:
        return self._pos_manager


class MockContextProvider:
    def __init__(
        self,
        settings: Settings,
        http_client: httpx2.AsyncClient,
        pos_manager: FakePOSManager,
    ) -> None:
        self._settings = settings
        self._http_client = http_client
        self._pos_manager = pos_manager

    def __call__(self, transaction: TransactionProtocol) -> MockContext:
        if not isinstance(transaction, MongoTransaction):
            raise RuntimeError()

        return MockContext(
            settings=self._settings,
            http_client=self._http_client,
            transaction=transaction,
            pos_manager=self._pos_manager,
        )


class ContextProviderOverride:
    def __init__(self, context_provider: MockContextProvider) -> None:
        self.context_provider = context_provider

    def __call__(self) -> MockContextProvider:
        return self.context_provider
