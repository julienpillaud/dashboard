import pytest
from cleanstack.mongo import MongoDocument
from fastapi import status
from fastapi.testclient import TestClient
from pymongo.database import Database

from app.domain.security import hash_refresh_token
from tests.plugins.users import TestUser


@pytest.mark.parametrize("user", [{"refresh_token": False}], indirect=True)
@pytest.mark.parametrize("client", [{"authenticated": False}], indirect=True)
def test_access_token(
    client: TestClient,
    user: TestUser,
    database: Database[MongoDocument],
) -> None:
    response = client.post(
        "/api/auth/token",
        data={"username": user.name, "password": user.password},
    )

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    new_raw_token = result["refresh_token"]
    new_hashed_token = hash_refresh_token(new_raw_token)

    # New token created
    new_db_token = database["refresh_tokens"].find_one({"hash_value": new_hashed_token})
    assert new_db_token is not None
    assert new_db_token["user_id"] == user.id
    assert new_db_token["revoked_at"] is None


@pytest.mark.parametrize("client", [{"authenticated": False}], indirect=True)
def test_token_bad_credentials(
    client: TestClient,
    database: Database[MongoDocument],
) -> None:
    response = client.post(
        "/api/auth/token",
        data={"username": "test", "password": "test"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    result = response.json()
    assert result["detail"] == "Not authenticated"

    refresh_token = database["refresh_tokens"].find().to_list()
    assert not refresh_token
