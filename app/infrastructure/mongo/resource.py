from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from cleanstack.mongo import MongoDocument
from pydantic import BaseModel, ConfigDict
from pymongo import AsyncMongoClient, MongoClient
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.database import Database

from app.core.settings import Settings
from app.infrastructure.mongo.logger import logger


class AsyncMongoResource(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: AsyncMongoClient[MongoDocument]
    database: AsyncDatabase[MongoDocument]

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
        )

    async def start_transaction(self) -> AsyncClientSession:
        session = self.client.start_session()
        await session.start_transaction()
        return session

    @staticmethod
    async def end_transaction(
        session: AsyncClientSession,
        exc_val: BaseException | None,
    ) -> None:
        if session.in_transaction:
            if exc_val is None:
                await session.commit_transaction()
                logger.info("Transaction committed")
            else:
                await session.abort_transaction()
                logger.info("Transaction aborted")
        await session.end_session()

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncClientSession]:
        async with self.client.start_session() as session:
            async with await session.start_transaction():
                yield session

    async def release(self) -> None:
        logger.info("MongoDB client released")
        await self.client.close()


class MongoResource(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: MongoClient[MongoDocument]
    database: Database[MongoDocument]

    @classmethod
    def from_settings(cls, settings: Settings, /) -> MongoResource:
        client: MongoClient[MongoDocument] = MongoClient(
            host=str(settings.mongo_uri),
            uuidRepresentation="standard",
        )
        client.admin.command("ping")
        logger.info("MongoDB client up")
        return cls(
            client=client,
            database=client[settings.mongo_database],
        )
