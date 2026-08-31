import datetime

from cleanstack import EntityId
from cleanstack.mongo import AsyncMongoRepository

from app.domain.refresh_tokens.entities import RefreshToken
from app.domain.refresh_tokens.repository import RefreshTokenRepositoryProtocol


class RefreshTokenRepository(
    AsyncMongoRepository[RefreshToken],
    RefreshTokenRepositoryProtocol,
):
    domain_entity_type = RefreshToken
    collection_name = "refresh_tokens"

    async def get_by_hash(self, value: str, /) -> RefreshToken | None:
        result = await self.collection.find_one({"hash_value": value})
        return self.to_domain_entity(result) if result else None

    async def revoke(self, token_id: EntityId) -> None:
        await self.collection.update_one(
            {"_id": token_id},
            {"$set": {"revoked_at": datetime.datetime.now(datetime.UTC)}},
        )

    async def revoke_for_user(self, user_id: EntityId) -> None:
        await self.collection.update_many(
            {"user_id": user_id, "revoked_at": None},
            {"$set": {"revoked_at": datetime.datetime.now(datetime.UTC)}},
        )
