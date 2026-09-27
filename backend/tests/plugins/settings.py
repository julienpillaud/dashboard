import secrets

import pytest

from app.core.settings import AppEnvironment, Settings


class SettingsOverride:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def __call__(self) -> Settings:
        return self.settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings(
        environment=AppEnvironment.TESTING,
        secret_key=secrets.token_urlsafe(32),
        mongo_user="user",
        mongo_password="password",
        mongo_host="localhost",
        mongo_database="test",
        mongo_local=True,
        gotenberg_host="http://localhost:3000",
    )
