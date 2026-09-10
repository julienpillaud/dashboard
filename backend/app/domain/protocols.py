from collections.abc import AsyncIterator
from typing import Protocol

from app.domain.articles.entities import RawArticle
from app.domain.categories.entities import RawCategory
from app.domain.taxes.entities import RawTax


class POSManagerProtocol(Protocol):
    async def get_taxes(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawTax]: ...

    async def get_categories(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawCategory]: ...

    async def get_articles(
        self,
        limit: int = 100,
        skip: int = 0,
    ) -> list[RawArticle]: ...


class PDFConverterProtocol(Protocol):
    def stream_pdf(
        self,
        html: str,
        /,
        timeout: float = 60,
        chunk_size: int = 65536,
    ) -> AsyncIterator[bytes]: ...
