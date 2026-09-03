from pydantic import BaseModel

from app.domain.synchronization.entities import FieldChange


def compute_changes[T: BaseModel](old: T, new: T) -> list[FieldChange]:
    changes = []
    for (key, old_value), (_, new_value) in zip(old, new, strict=True):
        if old_value != new_value:
            changes.append(
                FieldChange(
                    field=key,
                    old_value=old_value,
                    new_value=new_value,
                )
            )
    return changes
