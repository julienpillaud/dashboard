# from app.domain.entities import DomainEntity
# from app.infrastructure.mongo.types import MongoDocument
# from app.infrastructure.mongo.utils import normalize_ids
#
#
# class MongoMixin[T: DomainEntity]:
#     domain_entity_type: type[T]
#
#     @staticmethod
#     def to_database_entity(entity: T, /) -> MongoDocument:
#         document = entity.model_dump(exclude={"id"})
#         document["_id"] = entity.id
#         return document
#
#     def to_domain_entity(self, document: MongoDocument, /) -> T:
#         normalize_ids(document)
#         return self.domain_entity_type.model_validate(document)
