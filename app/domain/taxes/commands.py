import uuid

from cleanstack import FilterEntity, PaginatedResponse

from app.domain.context import ContextProtocol
from app.domain.exceptions import NotFoundError
from app.domain.logger import logger
from app.domain.stores.entities import Store
from app.domain.taxes.entities import RawTax, Tax


async def get_raw_taxes_command(
    context: ContextProtocol,
    /,
    current_store: Store,
    limit: int = 100,
    skip: int = 0,
) -> list[RawTax]:
    return await context.pos_manager.get_taxes(current_store, limit=limit, skip=skip)


async def get_taxes_command(
    context: ContextProtocol,
    /,
    current_store: Store,
) -> PaginatedResponse[Tax]:
    return await context.tax_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(current_store.id))],
    )


async def get_tax_command(
    context: ContextProtocol,
    /,
    current_store: Store,
    external_id: str,
) -> Tax:
    tax = await context.tax_repository.get_by_external_id(
        current_store,
        external_id=external_id,
    )
    if not tax:
        raise NotFoundError("Tax not found")

    return tax


async def synchronize_taxes_command(
    context: ContextProtocol,
    /,
    current_store: Store,
) -> None:
    raw_taxes = await context.pos_manager.get_taxes(current_store)
    raw_taxes_ids = {tax.id for tax in raw_taxes}

    taxes = await context.tax_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(current_store.id))],
    )
    taxes_map = {tax.external_id: tax for tax in taxes.items}

    for raw_tax in raw_taxes:
        if raw_tax.id not in taxes_map:
            logger.info(f"Synchronization: Creating tax: {raw_tax.name}")
            await create_tax(context, current_store, raw_tax=raw_tax)
        else:
            raw_taxes_ids.discard(raw_tax.id)
            tax = taxes_map[raw_tax.id]
            if tax.raw.updated_at != raw_tax.updated_at:
                logger.info(f"Synchronization: Updating tax: {raw_tax.name}")
                await update_tax(context, tax=tax, raw_tax=raw_tax)


async def create_tax(
    context: ContextProtocol,
    /,
    current_store: Store,
    raw_tax: RawTax,
) -> Tax:
    tax = Tax(
        id=uuid.uuid7(),
        store_id=current_store.id,
        external_id=raw_tax.id,
        raw=raw_tax,
    )
    await context.tax_repository.save(tax)
    return tax


async def update_tax(
    context: ContextProtocol,
    /,
    tax: Tax,
    raw_tax: RawTax,
) -> Tax:
    tax.raw = raw_tax
    await context.tax_repository.update(tax)
    return tax
