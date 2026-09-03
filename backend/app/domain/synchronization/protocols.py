from collections.abc import Sequence
from typing import Protocol

from app.domain.entities import BaseRawEntity, DomainEntity
from app.domain.synchronization.entities import FieldChange


class EntityUpdateProtocol(Protocol):
    @property
    def entity(self) -> DomainEntity: ...
    @property
    def raw_entity(self) -> BaseRawEntity: ...
    @property
    def changes(self) -> list[FieldChange]: ...


class SynchronizationPlanProtocol(Protocol):
    @property
    def to_create(self) -> Sequence[BaseRawEntity]: ...
    @property
    def to_update(self) -> Sequence[EntityUpdateProtocol]: ...
    @property
    def to_delete(self) -> Sequence[DomainEntity]: ...
