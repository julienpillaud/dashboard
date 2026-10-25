import datetime
import uuid
from decimal import ROUND_HALF_UP, Decimal

from cleanstack import EntityId, Pagination

from app.domain.articles.entities import ArticleDeposit
from app.domain.articles.use_cases import synchronize_articles
from app.domain.context import ContextProtocol
from app.domain.entities import DecimalType
from app.domain.exceptions import NotFoundError, ServiceUnavailableError
from app.domain.inventories.entities import (
    Inventory,
    InventoryAmounts,
    InventoryRecord,
    InventorySummary,
)
from app.domain.inventories.utils import Report


async def get_inventories(
    context: ContextProtocol,
    /,
    store_id: EntityId,
) -> list[InventorySummary]:
    return await context.inventory_repository.get_summaries_by_store(store_id)


async def get_inventory_by_id(
    context: ContextProtocol,
    /,
    store_id: EntityId,
    inventory_id: EntityId,
) -> Inventory:
    store = await context.store_repository.get_by_id(store_id)
    if not store:
        raise NotFoundError("Store not found")

    inventory = await context.inventory_repository.get_by_id(inventory_id)
    if not inventory:
        raise NotFoundError("Inventory not found")

    return inventory


async def create_inventory(
    context: ContextProtocol,
    /,
    store_id: EntityId,
) -> Inventory:
    store = await context.store_repository.get_by_id(store_id)
    if not store:
        raise NotFoundError("Store not found")

    synchronization = await synchronize_articles(context)
    if store.slug in synchronization.failed_stores:
        raise ServiceUnavailableError(
            f"Failed to synchronize articles for store {store.name}"
        )

    articles = await context.article_repository.get_all(
        pagination=Pagination(size=3000),
    )

    records = []
    report = Report()
    for article in articles.items:
        pos_article = article.store_mapping[str(store.id)]
        if (
            not pos_article.raw
            or pos_article.raw.stock_quantity is None
            or pos_article.raw.stock_quantity <= 0
        ):
            continue

        inventory_amount = get_inventory_value(
            total_cost=article.total_cost,
            stock_quantity=pos_article.raw.stock_quantity,
        )
        deposit_amount = (
            get_deposit_value(
                deposit=article.details.deposit,
                stock_quantity=pos_article.raw.stock_quantity,
            )
            if article.details.deposit
            else Decimal(0)
        )
        report.add(
            article.category,
            article.tax_rate,
            inventory_amount,
            deposit_amount,
        )

        record = InventoryRecord(
            article_id=article.id,
            pos_article_id=pos_article.raw.id,
            name=pos_article.raw.name,
            category=article.category,
            tax_rate=article.tax_rate,
            stock_quantity=pos_article.raw.stock_quantity,
            total_cost=article.total_cost,
            deposit=article.details.deposit,
            amounts=InventoryAmounts(
                amount=inventory_amount,
                deposit_amount=deposit_amount,
            ),
        )
        records.append(record)

    sorted_records = sorted(records, key=lambda x: (x.category, x.name))
    inventory = Inventory(
        id=uuid.uuid7(),
        store_id=store.id,
        store_name=store.name,
        created_at=datetime.datetime.now(datetime.UTC),
        amounts=InventoryAmounts(
            amount=report.total_inventory_value,
            deposit_amount=report.total_deposit_value,
        ),
        articles_count=sum(article.stock_quantity for article in records),
        category_summary=report.to_category_summary(),
        tax_summary=report.to_tax_summary(),
        records=sorted_records,
    )
    await context.inventory_repository.save(inventory)
    return inventory


def get_inventory_value(total_cost: DecimalType, stock_quantity: int) -> DecimalType:
    value = total_cost * Decimal(stock_quantity)
    return value.quantize(Decimal(".0001"), rounding=ROUND_HALF_UP)


def get_deposit_value(deposit: ArticleDeposit, stock_quantity: int) -> DecimalType:
    if deposit.crate and deposit.packaging:
        value = (deposit.crate * Decimal(stock_quantity)) / Decimal(deposit.packaging)
        return value.quantize(Decimal(".0001"), rounding=ROUND_HALF_UP)

    value = deposit.unit * Decimal(stock_quantity)
    return value.quantize(Decimal(".0001"), rounding=ROUND_HALF_UP)
