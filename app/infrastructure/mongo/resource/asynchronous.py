from cleanstack.mongo import MongoDocument
from pydantic import BaseModel, ConfigDict
from pymongo import AsyncMongoClient
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.core.settings import Settings
from app.infrastructure.mongo.logger import logger


class AsyncMongoResource(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: AsyncMongoClient[MongoDocument]
    database: AsyncDatabase[MongoDocument]
    supports_transaction: bool

    @classmethod
    async def from_settings(cls, settings: Settings, /) -> AsyncMongoResource:
        client: AsyncMongoClient[MongoDocument] = AsyncMongoClient(
            host=str(settings.mongo_uri),
            uuidRepresentation="standard",
        )
        await client.admin.command("ping")
        logger.info("MongoDB client up")
        return cls(
            client=client,
            database=client[settings.mongo_database],
            supports_transaction=settings.supports_transactions,
        )

    async def start_transaction(
        self,
        transactional: bool,
    ) -> AsyncClientSession | None:
        if not self.supports_transaction or not transactional:
            return None

        session = self.client.start_session()
        await session.start_transaction()
        return session

    @staticmethod
    async def end_transaction(
        session: AsyncClientSession | None,
        exc_val: BaseException | None,
        transactional: bool,
    ) -> None:
        if not session:
            return

        if session.in_transaction:
            if exc_val:
                await session.abort_transaction()
                logger.info(
                    f"Transaction rollback: {type(exc_val).__name__}({exc_val})"
                )
            elif transactional:
                await session.commit_transaction()
                logger.info("Transaction committed")

        await session.end_session()

    async def release(self) -> None:
        logger.info("MongoDB client released")
        await self.client.close()
