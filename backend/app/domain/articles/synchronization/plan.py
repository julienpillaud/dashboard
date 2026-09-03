from app.domain.articles.entities import Article, RawArticle
from app.domain.articles.synchronization.entities import (
    ArticleSynchronizationPlan,
    ArticleUpdate,
)
from app.domain.logger import logger
from app.domain.synchronization.utils import compute_changes


def build_synchronization_plan(
    raw_articles: list[RawArticle],
    articles: list[Article],
) -> ArticleSynchronizationPlan:
    to_create: list[RawArticle] = []
    to_update: list[ArticleUpdate] = []
    to_delete: list[Article] = []

    articles_map = {article.raw.id: article for article in articles}
    for raw_article in raw_articles:
        article = articles_map.get(raw_article.id)

        if article is None:
            logger.info(f"Synchronization: Creating article: {raw_article.name}")
            to_create.append(raw_article)
            continue

        if (
            article.raw.updated_at != raw_article.updated_at
            or article.raw.stock_quantity != raw_article.stock_quantity
        ):
            logger.info(f"Synchronization: Updating article: {raw_article.name}")
            changes = compute_changes(old=article.raw, new=raw_article)
            to_update.append(
                ArticleUpdate(
                    entity=article,
                    raw_entity=raw_article,
                    changes=changes,
                )
            )

    raw_ids = {raw_article.id for raw_article in raw_articles}
    for article_raw_id, article in articles_map.items():
        if article_raw_id not in raw_ids:
            logger.info(f"Synchronization: Deleting article: {article.raw.name}")
            to_delete.append(article)

    return ArticleSynchronizationPlan(
        to_create=to_create,
        to_update=to_update,
        to_delete=to_delete,
    )
