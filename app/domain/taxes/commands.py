from cleanstack import FilterEntity, PaginatedResponse

from app.domain.context import ContextProtocol
from app.domain.exceptions import NotFoundError
from app.domain.logger import logger
from app.domain.stores.entities import Store
from app.domain.taxes.entities import Tax
from app.domain.taxes.utils import create_tax, update_tax


async def get_taxes_command(
    context: ContextProtocol,
    /,
    store_slug: str | None = None,
) -> PaginatedResponse[Tax]:
    filters = []
    if store_slug:
        store = await context.store_repository.get_by_slug(slug=store_slug)
        if not store:
            raise NotFoundError("Store not found")
        filters.append(FilterEntity(field="store_id", value=str(store.id)))

    return await context.tax_repository.get_all(filters=filters)


async def get_tax_command(
    context: ContextProtocol,
    /,
    store: Store,
    external_id: str,
) -> Tax:
    tax = await context.tax_repository.get_by_external_id(
        store,
        external_id=external_id,
    )
    if not tax:
        raise NotFoundError("Tax not found")

    return tax


async def synchronize_taxes_command(
    context: ContextProtocol,
    /,
    store_slug: str,
) -> None:
    store = await context.store_repository.get_by_slug(slug=store_slug)
    if not store:
        raise NotFoundError("Store not found")

    pos_manager = context.get_pos_manager(store=store)
    raw_taxes = await pos_manager.get_taxes()
    response = await context.tax_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(store.id))],
    )
    taxes_map = {tax.raw.id: tax for tax in response.items}

    to_create = []
    to_update = []
    for raw_tax in raw_taxes:
        if raw_tax.id not in taxes_map:
            logger.info(f"Synchronization: Creating tax: {raw_tax.name}")
            to_create.append(raw_tax)
        else:
            tax = taxes_map[raw_tax.id]
            if tax.raw.updated_at != raw_tax.updated_at:
                logger.info(f"Synchronization: Updating tax: {raw_tax.name}")
                to_update.append((tax, raw_tax))

    await create_tax(context, store, to_create=to_create)
    await update_tax(context, to_update=to_update)
