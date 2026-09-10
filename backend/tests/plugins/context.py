from collections.abc import Iterator

import httpx2
import pytest

from app.core.settings import Settings
from tests.fakes.context import FakeContextProvider
from tests.fakes.pos_manager import FakePOSManager


@pytest.fixture(scope="session")
def fake_pos_manager() -> FakePOSManager:
    return FakePOSManager()


@pytest.fixture(autouse=True)
def _reset_fake_pos_manager(fake_pos_manager: FakePOSManager) -> Iterator[None]:
    yield
    fake_pos_manager.reset()


@pytest.fixture(scope="session")
def context_provider(
    settings: Settings,
    fake_pos_manager: FakePOSManager,
) -> FakeContextProvider:
    return FakeContextProvider(
        settings=settings,
        http_client=httpx2.AsyncClient(),
        pos_manager=fake_pos_manager,
    )
