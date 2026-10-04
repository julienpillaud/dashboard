from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.app import create_fastapi_app
from app.api.dependencies.app import get_context_provider, get_settings
from app.core.settings import Settings
from tests.mocks.context import ContextProviderOverride, MockContextProvider
from tests.plugins.settings import SettingsOverride


@pytest.fixture(scope="session")
def app(settings: Settings, context_provider: MockContextProvider) -> FastAPI:
    app = create_fastapi_app(settings=settings)
    app.dependency_overrides[get_settings] = SettingsOverride(settings=settings)
    app.dependency_overrides[get_context_provider] = ContextProviderOverride(
        context_provider=context_provider
    )
    return app


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    # Use a context manager to ensure that the lifespan is called
    with TestClient(app) as client:
        yield client
