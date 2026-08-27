from cleanstack.mongo import AsyncMongoRepository

from app.domain.users.entities import User
from app.domain.users.repository import UserRepositoryProtocol


class UserRepository(AsyncMongoRepository[User], UserRepositoryProtocol):
    domain_entity_type = User
    collection_name = "users"

    async def get_by_name(self, name: str) -> User | None:
        result = await self.collection.find_one({"name": name})
        return self.to_domain_entity(result) if result else None
