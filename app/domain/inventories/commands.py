import datetime
import uuid
from decimal import ROUND_HALF_UP, Decimal
from typing import TypedDict

from cleanstack import EntityId, FilterEntity, PaginatedResponse, Pagination
from pydantic import BaseModel

from app.domain.articles.entities import ArticleDeposit
from app.domain.context import ContextProtocol
from app.domain.entities import DecimalType
from app.domain.exceptions import NotFoundError
from app.domain.inventories.entities import Inventory, InventoryAmounts, InventoryRecord


class ReportAmounts(TypedDict):
    amount: Decimal
    deposit_amount: Decimal


class Report(BaseModel):
    summary: dict[str, ReportAmounts] = {}
    tax_rate_summary: dict[str, ReportAmounts] = {}
    total_inventory_value: Decimal = Decimal(0)
    total_deposit_value: Decimal = Decimal(0)

    def add(
        self,
        category: str,
        tax_rate: float,
        inventory_value: Decimal,
        deposit_value: Decimal,
    ) -> None:
        if category not in self.summary:
            self.summary[category] = ReportAmounts(
                amount=Decimal(0),
                deposit_amount=Decimal(0),
            )
        self.summary[category]["amount"] += inventory_value
        self.summary[category]["deposit_amount"] += deposit_value

        tax_key = f"{tax_rate:g}"
        if tax_key not in self.tax_rate_summary:
            self.tax_rate_summary[tax_key] = ReportAmounts(
                amount=Decimal(0),
                deposit_amount=Decimal(0),
            )
        self.tax_rate_summary[tax_key]["amount"] += inventory_value
        self.tax_rate_summary[tax_key]["deposit_amount"] += deposit_value

        self.total_inventory_value += inventory_value
        self.total_deposit_value += deposit_value

    def to_category_summary(self) -> dict[str, InventoryAmounts]:
        return {
            category: InventoryAmounts(
                amount=values["amount"],
                deposit_amount=values["deposit_amount"],
            )
            for category, values in self.summary.items()
        }

    def to_tax_summary(self) -> dict[str, InventoryAmounts]:
        sorted_items = sorted(
            self.tax_rate_summary.items(), key=lambda item: float(item[0])
        )

        return {
            tax_rate: InventoryAmounts(
                amount=values["amount"],
                deposit_amount=values["deposit_amount"],
            )
            for tax_rate, values in sorted_items
        }


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


async def get_inventory_command(
    context: ContextProtocol, /, store_slug: str, inventory_id: EntityId
) -> Inventory:
    store = await context.store_repository.get_by_slug(slug=store_slug)
    if not store:
        raise NotFoundError("Store not found")

    inventory = await context.inventory_repository.get_by_id(inventory_id)
    if not inventory:
        raise NotFoundError("Inventory not found")

    return inventory


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
    report = Report()
    for article in response.items:
        if (
            not article.data
            or article.raw.stock_quantity is None
            or article.raw.stock_quantity <= 0
        ):
            continue

        inventory_amount = get_inventory_value(
            total_cost=article.data.total_cost,
            stock_quantity=article.raw.stock_quantity,
        )
        deposit_amount = (
            get_deposit_value(
                deposit=article.data.deposit,
                stock_quantity=article.raw.stock_quantity,
            )
            if article.data.deposit
            else Decimal(0)
        )
        report.add(
            article.category,
            article.tax_rate,
            inventory_amount,
            deposit_amount,
        )

        record = InventoryRecord(
            external_id=article.raw.id,
            name=article.raw.name,
            category=article.category,
            tax_rate=article.tax_rate,
            stock_quantity=article.raw.stock_quantity,
            total_cost=article.data.total_cost,
            deposit=article.data.deposit,
            amounts=InventoryAmounts(
                amount=inventory_amount,
                deposit_amount=deposit_amount,
            ),
        )
        records.append(record)

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
        records=records,
    )
    await context.inventory_repository.save(inventory)
    return inventory


def get_inventory_value(total_cost: DecimalType, stock_quantity: int) -> DecimalType:
    value = total_cost * Decimal(stock_quantity)
    return value.quantize(Decimal(".01"), rounding=ROUND_HALF_UP)


def get_deposit_value(deposit: ArticleDeposit, stock_quantity: int) -> DecimalType:
    if deposit.crate and deposit.packaging:
        value = deposit.crate * (Decimal(stock_quantity) / Decimal(deposit.packaging))
        return value.quantize(Decimal(".01"), rounding=ROUND_HALF_UP)

    value = deposit.unit * Decimal(stock_quantity)
    return value.quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
