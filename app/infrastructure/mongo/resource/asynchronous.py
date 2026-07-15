from cleanstack.mongo import MongoDocument
from pydantic import BaseModel, ConfigDict
from pymongo import AsyncMongoClient
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.core.domain import TransactionProtocol
from app.core.settings import Settings
from app.infrastructure.mongo.logger import logger


class MongoResource(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: AsyncMongoClient[MongoDocument]
    database: AsyncDatabase[MongoDocument]

    @classmethod
    async def from_settings(cls, settings: Settings, /) -> MongoResource:
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


class MongoTransaction(TransactionProtocol):
    def __init__(self, resource: MongoResource, /) -> None:
        self.resource = resource
        self.session: AsyncClientSession | None = None

    async def start(self) -> None:
        self.session = self.resource.client.start_session()
        await self.session.start_transaction()

    async def end(self, error: BaseException | None) -> None:
        if not self.session:
            return

        if self.session.in_transaction:
            if error:
                await self.session.abort_transaction()
                logger.warning(f"Transaction rollback: {type(error).__name__}({error})")
            else:
                await self.session.commit_transaction()
                logger.info("Transaction committed")

        await self.session.end_session()
        self.session = None
