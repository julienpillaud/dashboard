# from pymongo.asynchronous.client_session import AsyncClientSession
# from pymongo.asynchronous.database import AsyncDatabase
#
# from app.domain.entities import DomainEntity
# from app.domain.stores.entities import Store
# from app.infrastructure.mongo.mixin import MongoMixin
# from app.infrastructure.mongo.types import MongoDocument
#
#
# class MongoRepositoryError(Exception):
#     pass
#
#
# class MongoRepository[T: DomainEntity](MongoMixin[T]):
#     collection_name: str
#
#     def __init__(
#         self,
#         database: AsyncDatabase[MongoDocument],
#         session: AsyncClientSession | None = None,
#     ) -> None:
#         self.database = database
#         self.collection = self.database[self.collection_name]
#         self.session = session
#
#     async def get_all(self, current_store: Store) -> list[T]:
#         pipeline = [{"$match": {"store_id": current_store.id}}]
#         pipeline.extend(self.lookup)
#         cursor = await self.collection.aggregate(pipeline=pipeline)
#         entities = await cursor.to_list()
#         return [self.to_domain_entity(entity) for entity in entities]
#
#     async def save(self, entity: T, /) -> None:
#         db_entity = self.to_database_entity(entity)
#
#         result = await self.collection.insert_one(document=db_entity)
#         if not result.acknowledged:
#             raise MongoRepositoryError("Failed to insert entity")
#
#     async def update(self, entity: T, /) -> None:
#         db_entity = self.to_database_entity(entity)
#
#         result = await self.collection.replace_one(
#             filter={"_id": entity.id},
#             replacement=db_entity,
#         )
#         if not result.acknowledged:
#             raise MongoRepositoryError("Failed to update entity")
#
#     @property
#     def lookup(self) -> list[MongoDocument]:
#         return []
