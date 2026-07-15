from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.requests import Request
from fastapi.security import APIKeyCookie, OAuth2PasswordBearer

from app.api.auth.utils import decode_access_token
from app.api.dependencies.app import get_domain, get_settings
from app.api.errors import AuthorizationError, InvalidAccessToken
from app.core.domain import Domain
from app.core.settings import Settings
from app.domain.exceptions import NotFoundError
from app.domain.users.entities import UserExternal
from app.domain.users.use_cases import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)


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
        return await domain.run(get_user_by_id, user_id=access_payload.sub)
    except InvalidAccessToken, NotFoundError:
        return None
