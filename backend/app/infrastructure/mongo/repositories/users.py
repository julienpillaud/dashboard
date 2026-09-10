from cleanstack import EntityId
from cleanstack.mongo import AsyncMongoRepository, MongoDocument
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.domain.users.entities import User
from app.domain.users.repository import UserRepositoryProtocol


class UserRepository(UserRepositoryProtocol):
    domain_entity_type = User
    collection_name = "users"
    searchable_fields = ()

    def __init__(
        self,
        database: AsyncDatabase[MongoDocument],
        session: AsyncClientSession | None = None,
    ) -> None:
        self.repository = AsyncMongoRepository[User].from_binding(
            binding=self,
            database=database,
            session=session,
        )

    async def get_by_id(self, entity_id: EntityId, /) -> User | None:
        return await self.repository.get_by_id(entity_id)

    async def get_by_name(self, name: str) -> User | None:
        result = await self.repository.collection.find_one({"name": name})
        return self.repository.to_domain_entity(result) if result else None
