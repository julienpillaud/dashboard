from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, status
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm

from app.api.auth.utils import build_response_with_cookies, make_not_authenticated_error
from app.api.dependencies.app import QueryDomain, get_settings
from app.api.dependencies.user import get_current_user
from app.core.settings import Settings
from app.domain.exceptions import (
    InvalidRefreshTokenError,
    NotFoundError,
    UnauthorizedError,
)
from app.domain.users.entities import UserExternal
from app.domain.users.use_cases import (
    authenticate_user,
    create_user_session,
    logout_user,
    refresh_user_session,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Annotated[Settings, Depends(get_settings)],
    domain: QueryDomain,
) -> Response:
    try:
        current_user = await domain.run(
            authenticate_user,
            email=form_data.username,
            password=form_data.password,
        )
    except (NotFoundError, UnauthorizedError) as error:
        raise make_not_authenticated_error() from error

    user_session = await domain.run(
        create_user_session,
        settings=settings,
        user_id=current_user.id,
    )
    return build_response_with_cookies(
        settings=settings,
        content={"id": str(current_user.id)},
        session=user_session,
    )


@router.post("/refresh")
async def refresh_token_endpoint(
    refresh_token: Annotated[str | None, Cookie()],
    settings: Annotated[Settings, Depends(get_settings)],
    domain: QueryDomain,
) -> Response:
    if not refresh_token:
        raise make_not_authenticated_error()

    try:
        user_session = await domain.run(
            refresh_user_session,
            settings=settings,
            raw_value=refresh_token,
        )
    except InvalidRefreshTokenError as error:
        raise make_not_authenticated_error() from error

    return build_response_with_cookies(
        settings=settings,
        content="Session refreshed",
        session=user_session,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: Annotated[UserExternal, Depends(get_current_user)],
    domain: QueryDomain,
) -> None:
    await domain.run(logout_user, user_id=current_user.id)
