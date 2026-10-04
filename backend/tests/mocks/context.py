import httpx2

from app.core.context import Context
from app.core.protocols import UnitOfWorkProtocol
from app.domain.protocols import POSManagerProtocol
from app.domain.stores.entities import Store
from app.infrastructure.mongo.uow import MongoUnitOfWork
from app.infrastructure.tactill.factory import TactillClientFactory
from tests.mocks.pos_manager import FakePOSManager


class MockContext(Context):
    def __init__(
        self,
        http_client: httpx2.AsyncClient,
        uow: MongoUnitOfWork,
        pos_manager: FakePOSManager,
    ) -> None:
        super().__init__(
            uow=uow,
            tactill_factory=TactillClientFactory(http_client),
        )
        self._pos_manager = pos_manager

    async def get_pos_manager(self, store: Store) -> POSManagerProtocol:
        return self._pos_manager


class MockContextProvider:
    def __init__(
        self,
        http_client: httpx2.AsyncClient,
        pos_manager: FakePOSManager,
    ) -> None:
        self.http_client = http_client
        self.pos_manager = pos_manager

    def __call__(self, uow: UnitOfWorkProtocol) -> MockContext:
        if not isinstance(uow, MongoUnitOfWork):
            raise RuntimeError()

        return MockContext(
            http_client=self.http_client,
            uow=uow,
            pos_manager=self.pos_manager,
        )


class ContextProviderOverride:
    def __init__(self, context_provider: MockContextProvider) -> None:
        self.context_provider = context_provider

    def __call__(self) -> MockContextProvider:
        return self.context_provider
