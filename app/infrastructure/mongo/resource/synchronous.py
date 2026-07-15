from cleanstack.mongo import MongoDocument
from pydantic import BaseModel, ConfigDict
from pymongo import MongoClient
from pymongo.database import Database

from app.core.settings import Settings
from app.infrastructure.mongo.logger import logger


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

    def release(self) -> None:
        logger.info("MongoDB client released")
        self.client.close()

    def reset(self) -> None:
        for collection in self.database.list_collection_names():
            self.database[collection].delete_many({})
