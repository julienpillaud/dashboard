from collections import defaultdict

from cleanstack import (
    FilterEntity,
    PaginatedResponse,
    Pagination,
    SortEntity,
    SortOrder,
)

from app.domain.articles.entities import Article, ArticleGroup
from app.domain.articles.synchronization.persistence import persist_synchronization_plan
from app.domain.articles.synchronization.plan import build_synchronization_plan
from app.domain.context import ContextProtocol
from app.domain.exceptions import NotFoundError
from app.domain.synchronization.entities import SynchronizationResponse
from app.domain.synchronization.response import build_synchronization_response


async def get_articles(
    context: ContextProtocol,
    /,
    store_slug: str | None = None,
    filters: list[FilterEntity] | None = None,
    pagination: Pagination | None = None,
) -> PaginatedResponse[Article]:
    repo_filters = []
    if store_slug:
        store = await context.store_repository.get_by_slug(slug=store_slug)
        if not store:
            raise NotFoundError("Store not found")
        repo_filters.append(FilterEntity(field="store_id", value=str(store.id)))

    if filters:
        repo_filters.extend(filters)

    return await context.article_repository.get_all(
        filters=repo_filters,
        sort=[SortEntity(field="raw.name", order=SortOrder.ASC)],
        pagination=pagination,
    )


async def get_articles_by_group(
    context: ContextProtocol,
    /,
    pagination: Pagination | None = None,
) -> PaginatedResponse[ArticleGroup]:
    total_articles = await context.article_repository.count()
    response = await context.article_repository.get_all(
        pagination=Pagination(size=total_articles)
    )

    groups = defaultdict(list)
    for article in response.items:
        groups[article.group_id].append(article)

    all_groups = [
        ArticleGroup(group_id=group_id, articles=group_articles)
        for group_id, group_articles in groups.items()
    ]

    pagination = pagination or Pagination()
    total = len(all_groups)
    return PaginatedResponse(
        page=pagination.page,
        size=pagination.size,
        pages=pagination.pages(total),
        total=total,
        items=all_groups[pagination.skip : pagination.skip + pagination.size],
    )


async def synchronize_articles(
    context: ContextProtocol,
    /,
    store_slug: str,
    dry_run: bool = True,
) -> SynchronizationResponse:
    store = await context.store_repository.get_by_slug(slug=store_slug)
    if not store:
        raise NotFoundError("Store not found")

    pos_manager = context.get_pos_manager(store=store)
    raw_articles = await pos_manager.get_articles(limit=3000)

    total_articles = await context.article_repository.count(
        filters=[FilterEntity(field="store_id", value=str(store.id))]
    )
    response = await context.article_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(store.id))],
        pagination=Pagination(size=total_articles),
    )

    plan = build_synchronization_plan(
        raw_articles=raw_articles,
        articles=response.items,
    )
    if not dry_run:
        await persist_synchronization_plan(context, store=store, plan=plan)

    return build_synchronization_response(
        dry_run=dry_run,
        store_slug=store_slug,
        raw_items_count=len(raw_articles),
        items_count=len(response.items),
        plan=plan,
    )
