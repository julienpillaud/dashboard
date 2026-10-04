from pymongo.asynchronous.client_session import AsyncClientSession

from app.core.protocols import UnitOfWorkProtocol
from app.infrastructure.mongo.logger import logger
from app.infrastructure.mongo.resource import MongoResource


class MongoUnitOfWork(UnitOfWorkProtocol):
    def __init__(self, resource: MongoResource, /) -> None:
        self.resource = resource
        self.session: AsyncClientSession | None = None

    async def start(self, transactional: bool) -> None:
        if not transactional:
            return

        self.session = self.resource.client.start_session()
        await self.session.start_transaction()

    async def end(self, error: BaseException | None) -> None:
        if not self.session:
            return

        try:
            if error is None:
                await self.session.commit_transaction()
                logger.debug("Transaction committed")
            else:
                await self.session.abort_transaction()
                logger.warning("Transaction rollback")
        finally:
            await self.session.end_session()
