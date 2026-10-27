import datetime
from decimal import Decimal

from tactill import TactillColor

from app.domain.articles.entities import RawArticle
from app.domain.categories.entities import RawCategory
from app.domain.protocols import POSError, POSManagerProtocol
from app.domain.taxes.entities import RawTax
from tests.factories.utils import generate_raw_id


class FakePOSManager(POSManagerProtocol):
    def __init__(self) -> None:
        self.taxes: list[RawTax] = []
        self.categories: list[RawCategory] = []
        self.articles: list[RawArticle] = []
        # Ids of the articles passed to update_article, in call order
        self.update_calls: list[str] = []

    def reset(self) -> None:
        self.articles.clear()
        self.update_calls.clear()
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
        name: str,
        price: Decimal,
        reference: str,
    ) -> RawArticle:
        current_date = datetime.datetime.now(datetime.UTC)
        article = RawArticle(
            id=generate_raw_id(),
            name=name,
            deprecated=False,
            created_at=current_date,
            updated_at=current_date,
            category_id=category_id,
            taxes=[tax_id],
            icon_text="    ",
            color=TactillColor.GREEN,
            barcode=None,
            in_stock=True,
            reference=reference,
            full_price=price,
            stock_quantity=0,
        )
        self.articles.append(article)
        return article

    async def update_article(
        self,
        article_id: str,
        category_id: str,
        tax_id: str,
        name: str,
        price: Decimal,
        reference: str,
    ) -> RawArticle:
        self.update_calls.append(article_id)
        for index, existing in enumerate(self.articles):
            if existing.id == article_id:
                updated = existing.model_copy(
                    update={
                        "category_id": category_id,
                        "taxes": [tax_id],
                        "name": name,
                        "full_price": float(price),
                        "reference": reference,
                        "updated_at": datetime.datetime.now(datetime.UTC),
                    }
                )
                self.articles[index] = updated
                return updated

        raise POSError(f"Article {article_id} not found")

    def add_articles(self, articles: list[RawArticle]) -> None:
        self.articles.extend(articles)

    def add_categories(self, categories: list[RawCategory]) -> None:
        self.categories.extend(categories)

    def add_taxes(self, taxes: list[RawTax]) -> None:
        self.taxes.extend(taxes)
