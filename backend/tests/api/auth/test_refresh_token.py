import pytest
from cleanstack.mongo import MongoDocument
from fastapi import status
from fastapi.testclient import TestClient
from pymongo.synchronous.database import Database

from app.domain.security import hash_refresh_token
from tests.plugins.users import TestUser


@pytest.mark.parametrize("user", [{"refresh_token": True}], indirect=True)
@pytest.mark.parametrize("client", [{"authenticated": False}], indirect=True)
def test_refresh_token(
    client: TestClient,
    user: TestUser,
    database: Database[MongoDocument],
) -> None:
    assert user.token is not None

    response = client.post(
        "/api/auth/refresh",
        data={
            "grant_type": "refresh_token",
            "refresh_token": user.token.raw_value,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    new_raw_token = result["refresh_token"]
    new_hashed_token = hash_refresh_token(new_raw_token)

    # Previous token is revoked
    old_db_token = database["refresh_tokens"].find_one(
        {"hash_value": user.token.hash_value}
    )
    assert old_db_token is not None
    assert old_db_token["user_id"] == user.id
    assert old_db_token["revoked_at"] is not None

    # New token created
    new_db_token = database["refresh_tokens"].find_one({"hash_value": new_hashed_token})
    assert new_db_token is not None
    assert new_db_token["user_id"] == user.id
    assert new_db_token["revoked_at"] is None


@pytest.mark.parametrize("user", [{"refresh_token": False}], indirect=True)
@pytest.mark.parametrize("client", [{"authenticated": False}], indirect=True)
def test_refresh_token_not_found(
    client: TestClient,
    user: TestUser,
    database: Database[MongoDocument],
) -> None:
    response = client.post(
        "/api/auth/refresh",
        data={
            "grant_type": "refresh_token",
            "refresh_token": "user.token.raw_value",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("user", [{"refresh_token": True}], indirect=True)
@pytest.mark.parametrize("client", [{"authenticated": False}], indirect=True)
def test_refresh_token_reuse(
    client: TestClient,
    user: TestUser,
    database: Database[MongoDocument],
) -> None:
    assert user.token is not None

    # 1st rotation (Legitimate) -> revokes user.token
    res1 = client.post(
        "/api/auth/refresh",
        data={"grant_type": "refresh_token", "refresh_token": user.token.raw_value},
    )
    assert res1.status_code == status.HTTP_200_OK

    # 2nd rotation with SAME token (Attack/Re-use)
    res2 = client.post(
        "/api/auth/refresh",
        data={"grant_type": "refresh_token", "refresh_token": user.token.raw_value},
    )
    assert res2.status_code == status.HTTP_401_UNAUTHORIZED

    # Security check: ALL tokens for this user must now be revoked!
    active_tokens = database["refresh_tokens"].count_documents(
        {"user_id": user.id, "revoked_at": None}
    )
    assert active_tokens == 0
