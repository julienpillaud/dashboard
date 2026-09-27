import datetime
from decimal import Decimal

from tactill import TactillColor

from app.domain.articles.entities import Article, RawArticle
from app.domain.categories.entities import RawCategory
from app.domain.protocols import POSManagerProtocol
from app.domain.taxes.entities import RawTax
from tests.factories.utils import generate_raw_id


class FakePOSManager(POSManagerProtocol):
    def __init__(self) -> None:
        self.taxes: list[RawTax] = []
        self.categories: list[RawCategory] = []
        self.articles: list[RawArticle] = []

    def reset(self) -> None:
        self.articles.clear()
        self.categories.clear()
        self.taxes.clear()

    async def get_categories(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawCategory]:
        return self.categories

    async def get_taxes(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawTax]:
        return self.taxes

    async def get_articles(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawArticle]:
        return self.articles

    async def create_article(
        self,
        category_id: str,
        tax_id: str,
        price: Decimal,
        article: Article,
    ) -> RawArticle:
        current_date = datetime.datetime.now(datetime.UTC)
        return RawArticle(
            id=generate_raw_id(),
            name=article.name,
            deprecated=False,
            created_at=current_date,
            updated_at=current_date,
            category_id=category_id,
            taxes=[tax_id],
            icon_text="    ",
            color=TactillColor.GREEN,
            barcode=None,
            in_stock=True,
            reference=article.id.hex,
            full_price=price,
            stock_quantity=0,
        )

    def add_categories(self, categories: list[RawCategory]) -> None:
        self.categories.extend(categories)

    def add_taxes(self, taxes: list[RawTax]) -> None:
        self.taxes.extend(taxes)
