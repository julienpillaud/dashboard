from decimal import Decimal
from typing import TypedDict

from pydantic import BaseModel

from app.domain.inventories.entities import InventoryAmounts


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
