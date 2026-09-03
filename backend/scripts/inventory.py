import argparse
import asyncio
import csv
import datetime
import uuid
from decimal import Decimal
from pathlib import Path

import httpx2
from cleanstack import FilterEntity, Pagination
from pydantic import BaseModel

from app.core.context import Context
from app.core.settings import Settings
from app.domain.articles.entities import Article
from app.domain.context import ContextProtocol
from app.domain.exceptions import NotFoundError
from app.domain.inventories.entities import Inventory, InventoryAmounts, InventoryRecord
from app.domain.inventories.use_cases import get_deposit_value, get_inventory_value
from app.domain.inventories.utils import Report
from app.domain.stores.entities import Store
from app.infrastructure.mongo.resource.asynchronous import (
    MongoResource,
    MongoTransaction,
)


class InventoryFile(BaseModel):
    name: str
    category: str
    stock_quantity: int


def read_inventory(csv_file: Path) -> list[InventoryFile]:
    lines = []
    with open(csv_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for line in reader:
            lines.append(
                InventoryFile(
                    name=line["Nom de l'article"],
                    category=line["Catégorie"],
                    stock_quantity=int(line["Stock"]),
                )
            )

    return lines


async def get_context(settings: Settings) -> Context:
    resource = await MongoResource.from_settings(settings)
    transaction = MongoTransaction(resource)
    return Context(
        settings=settings,
        http_client=httpx2.AsyncClient(),
        transaction=transaction,
    )


async def create_inventory(
    context: ContextProtocol,
    /,
    inventory_file: list[InventoryFile],
    store: Store,
    articles: list[Article],
    created_at: datetime.datetime,
    dry_run: bool,
) -> None:
    articles_map = {
        (article.raw.name, article.category): article for article in articles
    }

    records = []
    report = Report()
    for item in inventory_file:
        article = articles_map.get((item.name, item.category))
        if not article:
            continue

        if not article.data or item.stock_quantity <= 0:
            continue

        inventory_amount = get_inventory_value(
            total_cost=article.data.total_cost,
            stock_quantity=item.stock_quantity,
        )
        deposit_amount = (
            get_deposit_value(
                deposit=article.data.deposit,
                stock_quantity=item.stock_quantity,
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
            stock_quantity=item.stock_quantity,
            total_cost=article.data.total_cost,
            deposit=article.data.deposit,
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
        created_at=created_at,
        amounts=InventoryAmounts(
            amount=report.total_inventory_value,
            deposit_amount=report.total_deposit_value,
        ),
        articles_count=sum(article.stock_quantity for article in records),
        category_summary=report.to_category_summary(),
        tax_summary=report.to_tax_summary(),
        records=sorted_records,
    )
    print(inventory.amounts)

    if not dry_run:
        await context.inventory_repository.save(inventory)


async def main(
    csv_file: Path,
    created_at: datetime.datetime,
    dry_run: bool,
) -> None:
    settings = Settings()
    context = await get_context(settings=settings)

    store = await context.store_repository.get_by_slug(slug="pessac")
    if not store:
        raise NotFoundError("Store not found")

    response = await context.article_repository.get_all(
        filters=[FilterEntity(field="store_id", value=str(store.id))],
        pagination=Pagination(size=3000),
    )

    await create_inventory(
        context,
        inventory_file=read_inventory(csv_file=csv_file),
        store=store,
        articles=response.items,
        created_at=created_at,
        dry_run=dry_run,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("created_at")
    parser.add_argument("--dry-run", type=bool, default=True)
    args = parser.parse_args()

    csv_file_arg = Path(args.csv_file)
    if not csv_file_arg.is_file():
        parser.error("CSV file not found")

    created_at_arg = datetime.datetime.strptime(args.created_at, "%Y-%m-%d")

    asyncio.run(
        main(
            csv_file=csv_file_arg,
            created_at=created_at_arg,
            dry_run=args.dry_run,
        )
    )
