from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.requests import Request
from fastapi.security import APIKeyCookie, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from pymongo.asynchronous.client_session import AsyncClientSession

from app.api.auth.utils import decode_access_token
from app.api.errors import AuthorizationError, InvalidAccessToken
from app.core.context import Context, ContextFactory
from app.core.domain import Domain
from app.core.settings import Settings
from app.domain.exceptions import NotFoundError
from app.domain.users.commands import get_user_command
from app.domain.users.entities import UserExternal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # ty:ignore[missing-argument]


@lru_cache
def get_templates(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Jinja2Templates:
    return Jinja2Templates(directory=settings.paths.templates)


async def get_current_user(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    domain: Annotated[Domain, Depends(get_domain)],
    bearer_token: Annotated[str | None, Depends(oauth2_scheme)],
    cookie_token: Annotated[str | None, Depends(cookie_scheme)],
) -> UserExternal:
    token = bearer_token or cookie_token
    if token:
        user = await _get_current_user(
            settings=settings,
            domain=domain,
            token=token,
        )
        if user:
            return user

    if cookie_token or "text/html" in request.headers.get("accept", ""):
        raise AuthorizationError("Authentication failed")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Bearer token is invalid",
    )


async def get_optional_current_user(
    settings: Annotated[Settings, Depends(get_settings)],
    domain: Annotated[Domain, Depends(get_domain)],
    cookie_token: Annotated[str | None, Depends(cookie_scheme)],
) -> UserExternal | None:
    return await _get_current_user(
        settings=settings,
        domain=domain,
        token=cookie_token,
    )


async def _get_current_user(
    settings: Settings,
    domain: Domain,
    token: str | None,
) -> UserExternal | None:
    if not token:
        return None

    try:
        access_payload = decode_access_token(settings=settings, value=token)
        return await domain.run(get_user_command, user_id=access_payload.sub)
    except InvalidAccessToken, NotFoundError:
        return None


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
