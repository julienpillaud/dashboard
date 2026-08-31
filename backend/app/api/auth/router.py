from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.auth.utils import (
    OAuth2RefreshTokenRequestForm,
    TokenResponse,
    make_not_authenticated_error,
)
from app.api.dependencies.app import get_domain, get_settings
from app.api.dependencies.user import get_current_user
from app.core.domain import Domain
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


@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Annotated[Settings, Depends(get_settings)],
    domain: Annotated[Domain, Depends(get_domain)],
) -> TokenResponse:
    try:
        current_user = await domain.run(
            authenticate_user,
            name=form_data.username,
            password=form_data.password,
        )
    except (NotFoundError, UnauthorizedError) as error:
        raise make_not_authenticated_error() from error

    user_session = await domain.run(
        create_user_session,
        settings=settings,
        user_id=current_user.id,
    )
    return TokenResponse(
        access_token=user_session.access_token,
        expires_in=settings.access_token_expire,
        refresh_token=user_session.refresh_token,
    )


@router.post("/refresh")
async def refresh_token(
    form_data: Annotated[OAuth2RefreshTokenRequestForm, Depends()],
    settings: Annotated[Settings, Depends(get_settings)],
    domain: Annotated[Domain, Depends(get_domain)],
) -> TokenResponse:
    try:
        user_session = await domain.run(
            refresh_user_session,
            settings=settings,
            raw_value=form_data.refresh_token,
        )
    except InvalidRefreshTokenError as error:
        raise make_not_authenticated_error() from error

    return TokenResponse(
        access_token=user_session.access_token,
        expires_in=settings.access_token_expire,
        refresh_token=user_session.refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: Annotated[UserExternal, Depends(get_current_user)],
    domain: Annotated[Domain, Depends(get_domain)],
) -> None:
    await domain.run(logout_user, user_id=current_user.id)
