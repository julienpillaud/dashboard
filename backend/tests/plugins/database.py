from collections.abc import Iterator

import pytest
from cleanstack.mongo import MongoDocument
from pymongo.database import Database

from app.core.settings import Settings
from app.infrastructure.mongo.resource.synchronous import MongoResource


@pytest.fixture(scope="session")
def resource(settings: Settings) -> Iterator[MongoResource]:
    resource = MongoResource.from_settings(settings)
    yield resource
    resource.release()


@pytest.fixture
def database(resource: MongoResource) -> Iterator[Database[MongoDocument]]:
    yield resource.database
    resource.reset()
