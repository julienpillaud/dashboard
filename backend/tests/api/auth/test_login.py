from cleanstack.mongo import MongoDocument
from fastapi import status
from fastapi.testclient import TestClient
from pymongo.database import Database

from app.domain.security import hash_refresh_token
from tests.plugins.users import TestUser


def test_login_success(
    client: TestClient,
    user: TestUser,
    database: Database[MongoDocument],
) -> None:
    response = client.post(
        "/api/auth/login",
        data={"username": user.email, "password": user.password},
    )

    assert response.status_code == status.HTTP_200_OK

    access_token = response.cookies["access_token"]
    assert access_token is not None
    refresh_token = response.cookies["refresh_token"]
    assert refresh_token is not None

    result = response.json()
    assert result["id"] == str(user.id)

    # New token created
    hashed_token = hash_refresh_token(refresh_token)
    new_db_token = database["refresh_tokens"].find_one({"hash_value": hashed_token})
    assert new_db_token is not None
    assert new_db_token["user_id"] == user.id
    assert new_db_token["revoked_at"] is None


def test_login_bad_credentials(
    client: TestClient,
    database: Database[MongoDocument],
) -> None:
    response = client.post(
        "/api/auth/login",
        data={"username": "test", "password": "test"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    result = response.json()
    assert result["detail"] == "Not authenticated"

    refresh_token = database["refresh_tokens"].find().to_list()
    assert not refresh_token
