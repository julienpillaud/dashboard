from pydantic import BaseModel

from app.domain.synchronization.entities import FieldChange
from app.domain.taxes.entities import RawTax, Tax


class TaxUpdate(BaseModel):
    entity: Tax
    raw_entity: RawTax
    changes: list[FieldChange]


class TaxSynchronizationPlan(BaseModel):
    to_create: list[RawTax]
    to_update: list[TaxUpdate]
    to_delete: list[Tax]
