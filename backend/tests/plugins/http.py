from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.app import create_fastapi_app
from app.api.dependencies.app import get_settings
from app.core.settings import Settings
from app.domain.security import generate_access_token
from tests.plugins.users import TestUser


class SettingsOverride:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def __call__(self) -> Settings:
        return self.settings


@pytest.fixture
def token(user: TestUser, settings: Settings) -> str:
    return generate_access_token(
        settings=settings,
        user_id=user.id,
    )


@pytest.fixture(scope="session")
def app(settings: Settings) -> FastAPI:
    app = create_fastapi_app(settings=settings)
    app.dependency_overrides[get_settings] = SettingsOverride(settings=settings)
    return app


@pytest.fixture
def client(
    request: pytest.FixtureRequest,
    token: str,
    app: FastAPI,
) -> Iterator[TestClient]:
    params = getattr(request, "param", {})
    authenticated = params.get("authenticated", True)

    # Use a context manager to ensure that the lifespan is called
    with TestClient(app) as client:
        if authenticated:
            client.headers["Authorization"] = f"Bearer {token}"
        yield client
