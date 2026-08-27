from app.domain.articles.entities import Article
from app.domain.protocols import RepositoryProtocol


class ArticleRepositoryProtocol(RepositoryProtocol[Article]):
    async def save_many(self, entities: list[Article], /) -> None: ...

    async def update_raw(self, entities: list[Article], /) -> None: ...

    async def update_data(self, entities: list[Article], /) -> None: ...
