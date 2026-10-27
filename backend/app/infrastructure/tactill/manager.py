from decimal import Decimal

from tactill import (
    ArticleCreate,
    ArticleUpdate,
    AsyncTactillClient,
    FilterEntity,
    TactillColor,
)
from tactill.exceptions import (
    TactillError,
)

from app.domain.articles.entities import RawArticle
from app.domain.categories.entities import RawCategory
from app.domain.protocols import (
    POSError,
    POSManagerProtocol,
)
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
        try:
            articles = await self.client.articles.get_all(
                limit=limit,
                skip=skip,
                filters=[
                    FilterEntity(field="is_default", value="false"),
                    FilterEntity(field="in_stock", value="true"),
                ],
            )
        except TactillError as error:
            raise POSError(str(error)) from error

        return [
            RawArticle.model_validate(article.model_dump())
            for article in articles
            if article.full_price is not None and article.stock_quantity is not None
        ]

    async def create_article(
        self,
        category_id: str,
        tax_id: str,
        name: str,
        price: Decimal,
        reference: str,
    ) -> RawArticle:
        article_create = ArticleCreate(
            category_id=category_id,
            taxes=[tax_id],
            name=name,
            icon_text="    ",
            color=TactillColor.GREEN,
            full_price=price,
            reference=reference,
        )
        try:
            result = await self.client.articles.create(data=article_create)
        except TactillError as error:
            raise POSError(str(error)) from error

        return RawArticle.model_validate(result.model_dump())

    async def update_article(
        self,
        article_id: str,
        category_id: str,
        tax_id: str,
        name: str,
        price: Decimal,
        reference: str,
    ) -> RawArticle:
        article_update = ArticleUpdate(
            category_id=category_id,
            taxes=[tax_id],
            name=name,
            color=TactillColor.GREEN,
            full_price=price,
            reference=reference,
        )
        try:
            await self.client.articles.update(
                article_id=article_id,
                data=article_update,
            )
            result = await self.client.articles.get(article_id=article_id)
        except TactillError as error:
            raise POSError(str(error)) from error

        return RawArticle.model_validate(result.model_dump())
