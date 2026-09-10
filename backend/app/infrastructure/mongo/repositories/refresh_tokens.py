import datetime

from cleanstack import EntityId
from cleanstack.mongo import AsyncMongoRepository, MongoDocument
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.domain.refresh_tokens.entities import RefreshToken
from app.domain.refresh_tokens.repository import RefreshTokenRepositoryProtocol


class RefreshTokenRepository(RefreshTokenRepositoryProtocol):
    domain_entity_type = RefreshToken
    collection_name = "refresh_tokens"
    searchable_fields = ()

    def __init__(
        self,
        database: AsyncDatabase[MongoDocument],
        session: AsyncClientSession | None = None,
    ) -> None:
        self.repository = AsyncMongoRepository[RefreshToken].from_binding(
            binding=self,
            database=database,
            session=session,
        )

    async def save(self, entity: RefreshToken, /) -> None:
        await self.repository.save(entity)

    async def get_by_hash(self, value: str, /) -> RefreshToken | None:
        result = await self.repository.collection.find_one({"hash_value": value})
        return self.repository.to_domain_entity(result) if result else None

    async def revoke(self, token_id: EntityId) -> None:
        await self.repository.collection.update_one(
            {"_id": token_id},
            {"$set": {"revoked_at": datetime.datetime.now(datetime.UTC)}},
        )

    async def revoke_for_user(self, user_id: EntityId) -> None:
        await self.repository.collection.update_many(
            {"user_id": user_id, "revoked_at": None},
            {"$set": {"revoked_at": datetime.datetime.now(datetime.UTC)}},
        )
