from cleanstack.mongo import MongoDocument
from pydantic import BaseModel, ConfigDict
from pymongo import AsyncMongoClient
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.core.domain import ResourceProtocol
from app.core.settings import Settings
from app.infrastructure.mongo.logger import logger


class MongoClient(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: AsyncMongoClient[MongoDocument]
    database: AsyncDatabase[MongoDocument]

    @classmethod
    async def from_settings(cls, settings: Settings, /) -> MongoClient:
        client: AsyncMongoClient[MongoDocument] = AsyncMongoClient(
            host=str(settings.mongo_uri),
            uuidRepresentation="standard",
        )
        await client.admin.command("ping")
        logger.info("MongoDB client up")
        return cls(
            client=client,
            database=client[settings.mongo_database],
        )

    async def release(self) -> None:
        logger.info("MongoDB client released")
        await self.client.close()


class AsyncMongoResource(ResourceProtocol):
    def __init__(self, mongo_client: MongoClient, /) -> None:
        self.client = mongo_client.client
        self.database = mongo_client.database
        self.session: AsyncClientSession | None = None

    async def start_transaction(self, transactional: bool) -> None:
        if transactional:
            self.session = self.client.start_session()
            await self.session.start_transaction()
        else:
            self.session = None

    async def end_transaction(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        transactional: bool,
    ) -> None:
        if not self.session:
            return

        if self.session.in_transaction:
            if exc_type and exc_val:
                await self.session.abort_transaction()
                logger.info(f"Transaction rollback: {exc_type.__name__}({exc_val})")
            elif transactional:
                await self.session.commit_transaction()
                logger.info("Transaction committed")

        await self.session.end_session()
        self.session = None
