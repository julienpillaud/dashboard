from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from app.core.context import ContextProvider
from app.core.domain import Domain, DomainScope
from app.core.protocols import ContextProviderProtocol, UnitOfWorkProtocol
from app.core.settings import Settings
from app.domain.protocols import PDFConverterProtocol
from app.infrastructure.gotenberg.converter import GotenbergPDFConverter
from app.infrastructure.mongo.uow import MongoUnitOfWork


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


def get_uow(request: Request) -> MongoUnitOfWork:
    resource = request.app.state.mongo_resource
    return MongoUnitOfWork(resource)


def get_context_provider(request: Request) -> ContextProviderProtocol:
    return ContextProvider(tactill_factory=request.app.state.tactill_factory)


class DomainProvider:
    def __init__(self, *, transactional: bool = False) -> None:
        self.transactional = transactional

    async def __call__(
        self,
        uow: Annotated[UnitOfWorkProtocol, Depends(get_uow)],
        context_provider: Annotated[
            ContextProviderProtocol, Depends(get_context_provider)
        ],
    ) -> AsyncIterator[Domain]:
        async with DomainScope(
            uow=uow,
            context_provider=context_provider,
            transactional=self.transactional,
        ) as domain:
            yield domain


QueryDomain = Annotated[Domain, Depends(DomainProvider(), scope="function")]
CommandDomain = Annotated[
    Domain,
    Depends(DomainProvider(transactional=True), scope="function"),
]
