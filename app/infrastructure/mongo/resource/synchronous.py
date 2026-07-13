from cleanstack.mongo import MongoDocument
from pydantic import BaseModel, ConfigDict
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.synchronous.client_session import ClientSession

from app.core.settings import Settings
from app.infrastructure.mongo.logger import logger


class MongoResource(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: MongoClient[MongoDocument]
    database: Database[MongoDocument]
    supports_transaction: bool

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
            supports_transaction=settings.supports_transactions,
        )

    def start_transaction(self) -> ClientSession | None:
        if not self.supports_transaction:
            return None

        session = self.client.start_session()
        session.start_transaction()
        return session

    @staticmethod
    def end_transaction(
        session: ClientSession | None,
        exc_val: BaseException | None,
        is_mutation: bool,
    ) -> None:
        if session is None:
            return

        if session.in_transaction:
            if exc_val:
                session.abort_transaction()
                logger.info(
                    f"Transaction rollback: {type(exc_val).__name__}({exc_val})"
                )
            elif is_mutation:
                session.commit_transaction()
                logger.info("Transaction committed")

        session.end_session()

    def release(self) -> None:
        logger.info("MongoDB client released")
        self.client.close()

    def reset(self) -> None:
        for collection in self.database.list_collection_names():
            self.database[collection].delete_many({})
