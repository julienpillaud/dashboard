from cleanstack import (
    SortEntity,
    SortOrder,
)
from cleanstack.mongo import AsyncMongoRepository, MongoDocument

from app.domain.articles.entities import Article
from app.domain.articles.repository import ArticleRepositoryProtocol


class ArticleRepository(AsyncMongoRepository[Article], ArticleRepositoryProtocol):
    domain_entity_type = Article
    collection_name = "articles"

    def sort_stage(self, sort: list[SortEntity] | None) -> list[MongoDocument]:
        if not sort:
            return []

        order_map = {SortOrder.ASC: 1, SortOrder.DESC: -1}
        sort_pipeline = {}
        for sort_entity in sort:
            sort_pipeline[sort_entity.field] = order_map[sort_entity.order]

        return [{"$sort": sort_pipeline}]

    async def save_many(self, entities: list[Article], /) -> None:
        db_entities = [self.to_database_entity(entity) for entity in entities]
        await self.collection.insert_many(
            documents=db_entities,
            session=self.session,
        )
