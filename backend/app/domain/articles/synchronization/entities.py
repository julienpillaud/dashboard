from pydantic import BaseModel

from app.domain.articles.entities import Article, RawArticle
from app.domain.synchronization.entities import FieldChange


class ArticleUpdate(BaseModel):
    entity: Article
    raw_entity: RawArticle
    changes: list[FieldChange]


class ArticleSynchronizationPlan(BaseModel):
    to_create: list[RawArticle]
    to_update: list[ArticleUpdate]
    to_delete: list[Article]
