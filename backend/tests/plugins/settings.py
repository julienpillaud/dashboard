import secrets

import pytest

from app.core.settings import Settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings(
        secret_key=secrets.token_urlsafe(32),
        access_token_expire=60,
        refresh_token_expire=120,
        mongo_user="user",
        mongo_password="password",
        mongo_host="localhost",
        mongo_database="test",
        mongo_local=True,
        gotenberg_host="http://localhost:3000",
    )
