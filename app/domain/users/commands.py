from cleanstack import EntityId

from app.domain.context import ContextProtocol
from app.domain.exceptions import ForbiddenError, NotFoundError
from app.domain.security import verify_password
from app.domain.users.entities import UserExternal


async def authenticate_user_command(
    context: ContextProtocol,
    /,
    name: str,
    password: str,
) -> UserExternal:
    user = await context.user_repository.get_by_name(name=name)
    if not user:
        raise NotFoundError("User not found")

    if not verify_password(password, user.hashed_password):
        raise ForbiddenError("User authentication failed")

    return UserExternal(id=user.id, name=user.name)


async def get_user_command(
    context: ContextProtocol,
    /,
    user_id: EntityId,
) -> UserExternal:
    user = await context.user_repository.get_by_id(user_id)
    if not user:
        raise NotFoundError("User not found")

    return UserExternal(id=user.id, name=user.name)
