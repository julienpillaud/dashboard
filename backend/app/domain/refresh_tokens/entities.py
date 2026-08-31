import datetime

from cleanstack import BaseEntity, EntityId

from app.domain.entities import DateTime


class RefreshToken(BaseEntity):
    hash_value: str
    user_id: EntityId
    created_at: DateTime
    expires_at: DateTime
    revoked_at: DateTime | None = None

    @property
    def is_valid(self) -> bool:
        return self.expires_at > datetime.datetime.now(datetime.UTC)
