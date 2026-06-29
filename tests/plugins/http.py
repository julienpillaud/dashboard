from collections.abc import Iterator

import pytest
from cleanstack.mongo import MongoDocument
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.database import Database

from app.api.app import create_fastapi_app
from app.api.auth.utils import generate_access_token
from app.core.settings import Settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()  # ty:ignore[missing-argument]


@pytest.fixture(scope="session")
def database(settings: Settings) -> Database[MongoDocument]:
    client: MongoClient[MongoDocument] = MongoClient(
        host=str(settings.mongo_uri),
        uuidRepresentation="standard",
    )
    return client[settings.mongo_database]


@pytest.fixture(scope="session")
def token(settings: Settings, database: Database[MongoDocument]) -> str:
    user = database["users"].find_one({"name": "Admin"})
    assert user is not None
    return generate_access_token(
        settings=settings,
        user_id=user["_id"],
    )


@pytest.fixture(scope="session")
def app(settings: Settings) -> FastAPI:
    return create_fastapi_app(settings=settings)


@pytest.fixture
def client(app: FastAPI, token: str) -> Iterator[TestClient]:
    # Use a context manager to ensure that the lifespan is called
    with TestClient(app) as client:
        client.headers["Authorization"] = f"Bearer {token}"
        yield client
