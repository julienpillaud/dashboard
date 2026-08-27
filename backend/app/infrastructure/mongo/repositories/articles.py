import uuid
from typing import Any

from cleanstack import FilterEntity, FilterOperator, SortEntity, SortOrder
from cleanstack.exceptions import InvalidFilterError
from cleanstack.mongo import AsyncMongoRepository, MongoDocument
from pymongo import UpdateOne

from app.domain.articles.entities import Article
from app.domain.articles.repository import ArticleRepositoryProtocol

ALLOWED_FILTERS = [
    "store_id",
    "category",
    "raw.name",
]


class ArticleRepository(
    AsyncMongoRepository[Article],
    ArticleRepositoryProtocol,
):
    domain_entity_type = Article
    collection_name = "articles"

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

            if filter_entity.field in {"category", "raw.name"}:
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

    async def save_many(self, entities: list[Article], /) -> None:
        if not entities:
            return

        db_entities = [self.to_database_entity(entity) for entity in entities]
        await self.collection.insert_many(
            documents=db_entities,
            session=self.session,
        )

    async def update_raw(self, entities: list[Article], /) -> None:
        if not entities:
            return

        requests = [
            UpdateOne(
                filter={"_id": entity.id},
                update={
                    "$set": {
                        "category": entity.category,
                        "tax_rate": entity.tax_rate,
                        "raw": entity.raw.model_dump(),
                        "synced_at": entity.synced_at,
                    },
                },
            )
            for entity in entities
        ]

        await self.collection.bulk_write(requests=requests, ordered=False)

    async def update_data(self, entities: list[Article], /) -> None:
        if not entities:
            return

        requests = [
            UpdateOne(
                filter={"_id": entity.id},
                update={
                    "$set": {"data": entity.data.model_dump() if entity.data else None}
                },
            )
            for entity in entities
        ]

        await self.collection.bulk_write(requests=requests, ordered=False)
