import secrets
import uuid

import pytest
from cleanstack.mongo import MongoDocument
from pydantic import BaseModel
from pymongo.synchronous.database import Database

from app.core.settings import Settings
from app.domain.security import generate_refresh_token, get_password_hash


class TestRefreshToken(BaseModel):
    raw_value: str
    hash_value: str


class TestUser(BaseModel):
    __test__ = False

    id: uuid.UUID
    name: str
    password: str
    hashed_password: str
    token: TestRefreshToken | None = None


@pytest.fixture
def user(
    request: pytest.FixtureRequest,
    settings: Settings,
    database: Database[MongoDocument],
) -> TestUser:
    params = getattr(request, "param", {})
    with_refresh_token = params.get("refresh_token", False)

    user_id = uuid.uuid7()
    user_token: TestRefreshToken | None = None

    if with_refresh_token:
        raw_value = secrets.token_urlsafe(32)
        token_obj = generate_refresh_token(
            settings=settings,
            raw_value=raw_value,
            user_id=user_id,
        )
        user_token = TestRefreshToken(
            raw_value=raw_value,
            hash_value=token_obj.hash_value,
        )

        doc = token_obj.model_dump(exclude={"id"})
        doc["_id"] = token_obj.id
        database["refresh_tokens"].insert_one(doc)

    user = TestUser(
        id=user_id,
        name="user",
        password="password",
        hashed_password=get_password_hash("password"),
        token=user_token,
    )

    database["users"].insert_one(
        {
            "_id": user.id,
            "name": user.name,
            "hashed_password": user.hashed_password,
        }
    )

    return user
