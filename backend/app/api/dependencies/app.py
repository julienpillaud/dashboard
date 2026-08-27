from collections.abc import AsyncIterator, Callable
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from app.core.context import ContextProvider
from app.core.domain import Domain, DomainContext, TransactionProtocol
from app.core.settings import Settings
from app.domain.context import ContextProtocol
from app.domain.protocols import PDFConverterProtocol
from app.infrastructure.gotenberg.converter import GotenbergPDFConverter
from app.infrastructure.mongo.resource.asynchronous import MongoTransaction


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_templates(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Jinja2Templates:
    return Jinja2Templates(directory=settings.paths.templates)


def get_pdf_converter(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> PDFConverterProtocol:
    http_client = request.app.state.http_client
    return GotenbergPDFConverter(
        client=http_client,
        host=settings.gotenberg_host,
    )


def get_mongo_transaction(request: Request) -> MongoTransaction:
    mongo_resource = request.app.state.mongo_resource
    return MongoTransaction(mongo_resource)


def get_context_provider(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> Callable[[TransactionProtocol], ContextProtocol]:
    return ContextProvider(
        settings=settings,
        http_client=request.app.state.http_client,
    )


async def get_domain(
    mongo_transaction: Annotated[MongoTransaction, Depends(get_mongo_transaction)],
    context_provider: Annotated[
        Callable[[TransactionProtocol], ContextProtocol],
        Depends(get_context_provider),
    ],
) -> AsyncIterator[Domain]:
    async with DomainContext(
        transaction=mongo_transaction,
        context_provider=context_provider,
    ) as domain:
        yield domain
