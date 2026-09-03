from app.domain.logger import logger
from app.domain.synchronization.utils import compute_changes
from app.domain.taxes.entities import RawTax, Tax
from app.domain.taxes.synchronisation.entities import TaxSynchronizationPlan, TaxUpdate


def build_synchronization_plan(
    raw_taxes: list[RawTax],
    taxes: list[Tax],
) -> TaxSynchronizationPlan:
    to_create: list[RawTax] = []
    to_update: list[TaxUpdate] = []
    to_delete: list[Tax] = []

    taxes_map = {article.raw.id: article for article in taxes}
    for raw_tax in raw_taxes:
        tax = taxes_map.get(raw_tax.id)

        if tax is None:
            logger.info(f"Synchronization: Creating tax: {raw_tax.name}")
            to_create.append(raw_tax)
            continue

        if tax.raw.updated_at != raw_tax.updated_at:
            logger.info(f"Synchronization: Updating tax: {raw_tax.name}")
            changes = compute_changes(old=tax.raw, new=raw_tax)
            to_update.append(
                TaxUpdate(
                    entity=tax,
                    raw_entity=raw_tax,
                    changes=changes,
                )
            )

    raw_ids = {raw_tax.id for raw_tax in raw_taxes}
    for tax_raw_id, tax in taxes_map.items():
        if tax_raw_id not in raw_ids:
            logger.info(f"Synchronization: Deleting tax: {tax.raw.name}")
            to_delete.append(tax)

    return TaxSynchronizationPlan(
        to_create=to_create,
        to_update=to_update,
        to_delete=to_delete,
    )
