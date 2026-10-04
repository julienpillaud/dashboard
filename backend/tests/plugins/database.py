from collections.abc import Iterator

import pytest
from cleanstack.mongo import MongoDocument
from pymongo import MongoClient
from pymongo.database import Database

from app.core.settings import Settings


@pytest.fixture(scope="session")
def mongo_database(settings: Settings) -> Iterator[Database[MongoDocument]]:
    client: MongoClient[MongoDocument] = MongoClient(
        host=str(settings.mongo_uri),
        uuidRepresentation="standard",
    )
    database = client[settings.mongo_database]

    yield database

    client.close()


@pytest.fixture
def database(
    mongo_database: Database[MongoDocument],
) -> Iterator[Database[MongoDocument]]:
    yield mongo_database

    for name in mongo_database.list_collection_names():
        mongo_database[name].delete_many({})
