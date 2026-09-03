import uuid

from app.domain.context import ContextProtocol
from app.domain.logger import logger
from app.domain.stores.entities import Store
from app.domain.taxes.entities import RawTax, Tax
from app.domain.taxes.synchronisation.entities import TaxSynchronizationPlan


async def persist_synchronization_plan(
    context: ContextProtocol,
    /,
    store: Store,
    plan: TaxSynchronizationPlan,
) -> None:
    await create_taxes(context, store=store, to_create=plan.to_create)
    await update_taxes(
        context,
        to_update=[(item.entity, item.raw_entity) for item in plan.to_update],
    )
    await delete_taxes(context, to_delete=plan.to_delete)


async def create_taxes(
    context: ContextProtocol,
    /,
    store: Store,
    to_create: list[RawTax],
) -> None:
    if not to_create:
        logger.info("Synchronization: No tax to create")
        return

    taxes = [
        Tax(
            id=uuid.uuid7(),
            store_id=store.id,
            store_name=store.name,
            raw=tax,
        )
        for tax in to_create
    ]
    await context.tax_repository.save_many(taxes)


async def update_taxes(
    context: ContextProtocol,
    /,
    to_update: list[tuple[Tax, RawTax]],
) -> None:
    if not to_update:
        logger.info("Synchronization: No tax to update")
        return

    taxes = []
    for tax, raw_tax in to_update:
        tax.raw = raw_tax
        taxes.append(tax)

    await context.tax_repository.update_many(taxes)


async def delete_taxes(
    context: ContextProtocol,
    /,
    to_delete: list[Tax],
) -> None:
    if not to_delete:
        logger.info("Synchronization: No tax to delete")
        return

    await context.tax_repository.delete_many(to_delete)
