from cleanstack import EntityId

from app.domain.context import ContextProtocol
from app.domain.exceptions import ForbiddenError, NotFoundError
from app.domain.security import verify_password
from app.domain.stores.entities import Store, StorePublic


async def authenticate_store_command(
    context: ContextProtocol,
    /,
    name: str,
    password: str,
) -> StorePublic:
    store = await context.store_repository.get_by_name(name=name)
    if not store:
        raise NotFoundError("Store not found")

    if not verify_password(password, store.hashed_password):
        raise ForbiddenError("Store authentication failed")

    return StorePublic(id=store.id, name=store.name, slug=store.slug)


async def get_store_command(context: ContextProtocol, /, store_id: EntityId) -> Store:
    store = await context.store_repository.get_by_id(store_id)
    if not store:
        raise NotFoundError("Store not found")

    return store
