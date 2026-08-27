from tactill import AsyncTactillClient, FilterEntity, FilterOperator

from app.domain.articles.entities import RawArticle
from app.domain.categories.entities import RawCategory
from app.domain.protocols import POSManagerProtocol
from app.domain.taxes.entities import RawTax
from app.infrastructure.tactill.data import CATEGORIES


class TactillManager(POSManagerProtocol):
    def __init__(self, client: AsyncTactillClient) -> None:
        self.client = client

    async def get_taxes(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawTax]:
        taxes = await self.client.taxes.get_all(limit=limit, skip=skip)
        return [RawTax.model_validate(tax.model_dump()) for tax in taxes]

    async def get_categories(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawCategory]:
        categories = await self.client.categories.get_all(
            limit=limit,
            skip=skip,
            filters=[
                FilterEntity(
                    field="name",
                    value=CATEGORIES,
                    operator=FilterOperator.IN,
                )
            ],
        )
        return [
            RawCategory.model_validate(category.model_dump()) for category in categories
        ]

    async def get_articles(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawArticle]:
        categories = await self.get_categories()
        category_ids = [category.id for category in categories]
        articles = await self.client.articles.get_all(
            limit=limit,
            skip=skip,
            filters=[
                FilterEntity(
                    field="category_id",
                    value=category_ids,
                    operator=FilterOperator.IN,
                )
            ],
        )
        return [RawArticle.model_validate(article.model_dump()) for article in articles]
