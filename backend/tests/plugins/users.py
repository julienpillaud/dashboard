import datetime
import secrets
import uuid

import pytest
from cleanstack.mongo import MongoDocument
from fastapi.testclient import TestClient
from pydantic import BaseModel, EmailStr
from pymongo.synchronous.database import Database

from app.core.settings import Settings
from app.domain.security import (
    generate_access_token,
    generate_refresh_token,
    get_password_hash,
)


class TestUser(BaseModel):
    __test__ = False

    id: uuid.UUID
    email: EmailStr
    password: str
    hashed_password: str
    access_token: str | None = None
    refresh_token: str | None = None


@pytest.fixture
def user(database: Database[MongoDocument]) -> TestUser:
    user_id = uuid.uuid7()
    user_password = "password"
    user = TestUser(
        id=user_id,
        email="user@email.fr",
        password=user_password,
        hashed_password=get_password_hash(user_password),
    )
    database["users"].insert_one(
        {
            "_id": user.id,
            "email": user.email,
            "hashed_password": user.hashed_password,
        }
    )
    return user


@pytest.fixture
def tokens(
    request: pytest.FixtureRequest,
    settings: Settings,
    database: Database[MongoDocument],
    user: TestUser,
    client: TestClient,
) -> None:
    params = getattr(request, "param", {"access": "valid", "refresh": "valid"})

    current_date = datetime.datetime.now(datetime.UTC)

    if params["access"] == "valid":
        access_token = generate_access_token(
            settings=settings,
            user_id=user.id,
            current_date=current_date,
        )
        client.cookies.set("access_token", access_token)
    elif params["access"] == "expired":
        expired_date = current_date - datetime.timedelta(days=30)
        access_token = generate_access_token(
            settings=settings,
            user_id=user.id,
            current_date=expired_date,
        )
        client.cookies.set("access_token", access_token)

        user.access_token = access_token

    if params["refresh"] != "none":
        raw_refresh_token = secrets.token_urlsafe(32)
        if params["refresh"] == "expired":
            token_date = current_date - datetime.timedelta(days=30)
        else:
            token_date = current_date

        refresh_token = generate_refresh_token(
            settings=settings,
            raw_value=raw_refresh_token,
            user_id=user.id,
            current_date=token_date,
        )

        if params["refresh"] == "revoked":
            refresh_token.revoked_at = current_date

        document = refresh_token.model_dump(exclude={"id"})
        document["_id"] = refresh_token.id
        database["refresh_tokens"].insert_one(document)

        user.refresh_token = raw_refresh_token
