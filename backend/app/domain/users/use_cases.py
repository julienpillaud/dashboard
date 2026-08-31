import datetime
import secrets

from cleanstack import EntityId

from app.core.settings import Settings
from app.domain.context import ContextProtocol
from app.domain.exceptions import (
    InvalidRefreshTokenError,
    NotFoundError,
    UnauthorizedError,
)
from app.domain.security import (
    generate_access_token,
    generate_refresh_token,
    hash_refresh_token,
    verify_password,
)
from app.domain.users.entities import UserExternal, UserSession


async def authenticate_user(
    context: ContextProtocol,
    /,
    name: str,
    password: str,
) -> UserExternal:
    user = await context.user_repository.get_by_name(name=name)
    if not user:
        raise NotFoundError(f"User '{name}' not found")

    if not verify_password(password, user.hashed_password):
        raise UnauthorizedError("User authentication failed")

    return UserExternal(id=user.id, name=user.name)


async def get_user_by_id(
    context: ContextProtocol,
    /,
    user_id: EntityId,
) -> UserExternal:
    user = await context.user_repository.get_by_id(user_id)
    if not user:
        raise NotFoundError("User not found")

    return UserExternal(id=user.id, name=user.name)


async def create_user_session(
    context: ContextProtocol,
    /,
    settings: Settings,
    user_id: EntityId,
) -> UserSession:
    current_date = datetime.datetime.now(datetime.UTC)
    access_token = generate_access_token(
        settings=settings,
        user_id=user_id,
        current_date=current_date,
    )
    raw_refresh_token = secrets.token_urlsafe(32)
    refresh_token = generate_refresh_token(
        settings=settings,
        raw_value=raw_refresh_token,
        user_id=user_id,
        current_date=current_date,
    )
    await context.refresh_token_repository.save(refresh_token)
    return UserSession(
        access_token=access_token,
        refresh_token=raw_refresh_token,
    )


async def refresh_user_session(
    context: ContextProtocol,
    /,
    settings: Settings,
    raw_value: str,
) -> UserSession:
    previous_token = await context.refresh_token_repository.get_by_hash(
        hash_refresh_token(raw_value)
    )
    if not previous_token:
        raise InvalidRefreshTokenError("Refresh token not found")

    if previous_token.revoked_at:
        await logout_user(context, user_id=previous_token.user_id)
        raise InvalidRefreshTokenError("Refresh token reuse detected")

    if not previous_token.is_valid:
        raise InvalidRefreshTokenError("Refresh token expired")

    await context.refresh_token_repository.revoke(token_id=previous_token.id)

    return await create_user_session(
        context,
        settings=settings,
        user_id=previous_token.user_id,
    )


async def logout_user(
    context: ContextProtocol,
    /,
    user_id: EntityId,
) -> None:
    await context.refresh_token_repository.revoke_for_user(user_id=user_id)
