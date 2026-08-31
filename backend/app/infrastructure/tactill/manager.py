from tactill import AsyncTactillClient, FilterEntity

from app.domain.articles.entities import RawArticle
from app.domain.categories.entities import RawCategory
from app.domain.protocols import POSManagerProtocol
from app.domain.taxes.entities import RawTax


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
        categories = await self.client.categories.get_all(limit=limit, skip=skip)
        return [
            RawCategory.model_validate(category.model_dump()) for category in categories
        ]

    async def get_articles(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawArticle]:
        articles = await self.client.articles.get_all(
            limit=limit,
            skip=skip,
            filters=[FilterEntity(field="is_default", value="false")],
        )
        return [RawArticle.model_validate(article.model_dump()) for article in articles]
