from app.domain.protocols import RepositoryProtocol
from app.domain.users.entities import User


class UserRepositoryProtocol(RepositoryProtocol[User]):
    async def get_by_name(self, name: str) -> User | None: ...
