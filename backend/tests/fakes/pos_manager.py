from app.domain.articles.entities import RawArticle
from app.domain.categories.entities import RawCategory
from app.domain.protocols import POSManagerProtocol
from app.domain.taxes.entities import RawTax


class FakePOSManager(POSManagerProtocol):
    def __init__(self) -> None:
        self.taxes: list[RawTax] = []
        self.categories: list[RawCategory] = []
        self.articles: list[RawArticle] = []

    def reset(self) -> None:
        self.articles.clear()
        self.categories.clear()
        self.taxes.clear()

    async def get_taxes(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawTax]:
        return self.taxes

    async def get_categories(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawCategory]:
        return self.categories

    async def get_articles(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawArticle]:
        return self.articles

    def add_taxes(self, taxes: list[RawTax]) -> None:
        self.taxes.extend(taxes)
