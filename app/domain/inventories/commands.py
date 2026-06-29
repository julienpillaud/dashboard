import datetime
import uuid
from collections import defaultdict
from decimal import Decimal

from cleanstack import FilterEntity, PaginatedResponse, Pagination

from app.domain.articles.entities import ArticleDeposit
from app.domain.context import ContextProtocol
from app.domain.entities import DecimalType
from app.domain.exceptions import NotFoundError
from app.domain.inventories.entities import Inventory, InventoryRecord, InventorySummary


async def get_inventories_command(
    context: ContextProtocol,
    /,
    store_slug: str,
    pagination: Pagination | None = None,
) -> PaginatedResponse[Inventory]:
    store = await context.store_repository.get_by_slug(slug=store_slug)
    if not store:
        raise NotFoundError("Store not found")

    return await context.inventory_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(store.id))],
        pagination=pagination,
    )


async def create_inventory_command(
    context: ContextProtocol,
    /,
    store_slug: str,
) -> Inventory:
    store = await context.store_repository.get_by_slug(slug=store_slug)
    if not store:
        raise NotFoundError("Store not found")

    response = await context.article_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(store.id))],
        pagination=Pagination(size=3000),
    )

    records = []
    summary = defaultdict(dict)
    for article in response.items:
        if not article.data or not article.raw.stock_quantity:
            continue

        inventory_value = get_inventory_value(
            total_cost=article.data.total_cost,
            stock_quantity=article.raw.stock_quantity,
        )
        summary[article.category]["inventory_value"] += inventory_value
        deposit_value = (
            get_deposit_value(
                deposit=article.data.deposit,
                stock_quantity=article.raw.stock_quantity,
            )
            if article.data.deposit
            else Decimal(0)
        )
        summary[article.category]["deposit_value"] += deposit_value

        record = InventoryRecord(
            external_id=article.raw.id,
            name=article.raw.name,
            category=article.category,
            stock_quantity=article.raw.stock_quantity,
            total_cost=article.data.total_cost,
            deposit=article.data.deposit,
            inventory_value=inventory_value,
            deposit_value=deposit_value,
        )
        records.append(record)

    inventory = Inventory(
        id=uuid.uuid7(),
        store_id=store.id,
        created_at=datetime.datetime.now(datetime.UTC),
        inventory_value=sum(summary.values()),
        deposit_value=sum(summary.values()),
        summary={
            category: InventorySummary(
                inventory_value=values["inventory_value"],
                deposit_value=values["deposit_value"],
            )
            for category, values in summary.items()
        },
        records=records,
    )
    await context.inventory_repository.save(inventory)
    return inventory


def get_inventory_value(total_cost: DecimalType, stock_quantity: int) -> DecimalType:
    return total_cost * Decimal(stock_quantity)


def get_deposit_value(deposit: ArticleDeposit, stock_quantity: int) -> DecimalType:
    if deposit.crate and deposit.packaging:
        return deposit.crate * (Decimal(stock_quantity) / Decimal(deposit.packaging))

    return deposit.unit * Decimal(stock_quantity)
