import uuid

from app.domain.context import ContextProtocol
from app.domain.stores.entities import Store
from app.domain.taxes.entities import RawTax, Tax


async def create_tax(
    context: ContextProtocol,
    /,
    current_store: Store,
    to_create: list[RawTax],
) -> None:
    taxes = [
        Tax(
            id=uuid.uuid7(),
            store_id=current_store.id,
            raw=tax,
        )
        for tax in to_create
    ]
    await context.tax_repository.save_many(taxes)


async def update_tax(
    context: ContextProtocol,
    /,
    to_update: list[tuple[Tax, RawTax]],
) -> None:
    taxes = []
    for tax, raw_tax in to_update:
        tax.raw = raw_tax
        taxes.append(tax)

    await context.tax_repository.update_many(taxes)
