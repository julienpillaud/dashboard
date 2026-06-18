import uuid
from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from pymongo.asynchronous.client_session import AsyncClientSession

from app.core.context import Context, ContextFactory
from app.core.domain import Domain
from app.core.settings import Settings
from app.domain.exceptions import NotFoundError
from app.domain.stores.commands import get_store_command
from app.domain.stores.entities import Store


class AuthorizationError(Exception):
    pass


@lru_cache
def get_settings() -> Settings:
    return Settings()  # ty:ignore[missing-argument]


@lru_cache
def get_templates(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Jinja2Templates:
    return Jinja2Templates(directory=settings.paths.templates)


async def get_current_store(
    request: Request,
    domain: Annotated[Domain, Depends(get_domain)],
) -> Store:
    store = await _get_current_store(request=request, domain=domain)
    if not store:
        raise AuthorizationError("Authentication failed")

    return store


async def get_optional_current_store(
    request: Request,
    domain: Annotated[Domain, Depends(get_domain)],
) -> Store | None:
    return await _get_current_store(request=request, domain=domain)


async def _get_current_store(request: Request, domain: Domain) -> Store | None:
    store_id = request.session.get("store_id")
    if not store_id:
        return None

    try:
        return await domain.run(get_store_command, store_id=uuid.UUID(store_id))
    except NotFoundError as error:
        raise AuthorizationError("User not found") from error


def get_context_factory(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> ContextFactory:
    mongo_client = request.app.state.mongo_resource.client
    http_client = request.app.state.http_client

    def _get_context(session: AsyncClientSession | None) -> Context:
        return Context(
            settings=settings,
            http_client=http_client,
            database=mongo_client[settings.mongo_database],
            session=session,
        )

    return _get_context


async def get_domain(
    request: Request,
    context_factory: Annotated[ContextFactory, Depends(get_context_factory)],
) -> AsyncIterator[Domain]:
    mongo_resource = request.app.state.mongo_resource
    async with Domain(
        resource=mongo_resource,
        context_factory=context_factory,
    ) as domain:
        yield domain
