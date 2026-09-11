import uuid
from typing import Any

from cleanstack import (
    FilterEntity,
    FilterOperator,
    PaginatedResponse,
    Pagination,
    SortEntity,
    SortOrder,
)
from cleanstack.exceptions import InvalidFilterError
from cleanstack.mongo import AsyncMongoRepository, MongoDocument
from pymongo import DeleteOne
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase

from app.domain.articles.entities import Article
from app.domain.articles.repository import ArticleRepositoryProtocol

ALLOWED_FILTERS = ["store_id", "category", "raw.name", "status"]


class ArticleMongoAdapter(AsyncMongoRepository[Article]):
    def filters_stage(self, filters: list[FilterEntity] | None) -> list[MongoDocument]:
        if not filters:
            return []

        filters_pipeline: dict[str, Any] = {}
        for filter_entity in filters:
            if filter_entity.field not in ALLOWED_FILTERS:
                raise InvalidFilterError("Invalid field")

            if filter_entity.operator != FilterOperator.EQ:
                raise InvalidFilterError("Invalid operator")

            if filter_entity.field == "store_id":
                assert isinstance(filter_entity.value, str)
                filters_pipeline[filter_entity.field] = {
                    "$eq": uuid.UUID(filter_entity.value)
                }

            if filter_entity.field in {"category", "raw.name", "status"}:
                assert isinstance(filter_entity.value, str)
                filters_pipeline[filter_entity.field] = {"$eq": filter_entity.value}

        return [{"$match": filters_pipeline}]

    def sort_stage(self, sort: list[SortEntity] | None) -> list[MongoDocument]:
        # Override to accept embedded fields (remove field check)
        if not sort:
            return []

        order_map = {SortOrder.ASC: 1, SortOrder.DESC: -1}
        sort_pipeline = {}
        for sort_entity in sort:
            sort_pipeline[sort_entity.field] = order_map[sort_entity.order]

        return [{"$sort": sort_pipeline}]


class ArticleRepository(ArticleRepositoryProtocol):
    domain_entity_type = Article
    collection_name = "articles"
    searchable_fields = ()

    def __init__(
        self,
        database: AsyncDatabase[MongoDocument],
        session: AsyncClientSession | None = None,
    ) -> None:
        self.repository = ArticleMongoAdapter.from_binding(
            binding=self,
            database=database,
            session=session,
        )

    async def get_all(
        self,
        search: str | None = None,
        filters: list[FilterEntity] | None = None,
        sort: list[SortEntity] | None = None,
        pagination: Pagination | None = None,
    ) -> PaginatedResponse[Article]:
        return await self.repository.get_all(
            search=search,
            filters=filters,
            sort=sort,
            pagination=pagination,
        )

    async def count(self, filters: list[FilterEntity] | None = None) -> int:
        count_pipeline = [*self.repository.filters_stage(filters), {"$count": "total"}]
        count_cursor = await self.repository.collection.aggregate(
            pipeline=count_pipeline,
            session=self.repository.session,
        )
        count_result = await count_cursor.try_next()
        return int(count_result["total"]) if count_result else 0

    async def save_many(self, entities: list[Article], /) -> None:
        if not entities:
            return

        db_entities = [
            self.repository.to_database_entity(entity) for entity in entities
        ]
        await self.repository.collection.insert_many(
            documents=db_entities,
            session=self.repository.session,
        )

    async def delete_many(self, entities: list[Article], /) -> None:
        if not entities:
            return

        requests = [DeleteOne(filter={"_id": entity.id}) for entity in entities]
        await self.repository.collection.bulk_write(requests=requests, ordered=False)
