from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from app.core.context import ContextProvider, ContextProviderType
from app.core.domain import BaseDomain, Domain
from app.core.settings import Settings
from app.domain.protocols import PDFConverterProtocol
from app.infrastructure.gotenberg.converter import GotenbergPDFConverter
from app.infrastructure.mongo.resource.asynchronous import AsyncMongoResource


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


def get_mongo_resource(request: Request) -> AsyncMongoResource:
    resource = request.app.state.mongo_resource
    if not isinstance(resource, AsyncMongoResource):
        raise RuntimeError()

    return resource


def get_context_provider(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    mongo_resource: Annotated[AsyncMongoResource, Depends(get_mongo_resource)],
) -> ContextProviderType:
    return ContextProvider(
        settings=settings,
        http_client=request.app.state.http_client,
        database=mongo_resource.client[settings.mongo_database],
    )


class DomainProvider:
    def __init__(self, *, transactional: bool = False) -> None:
        self._transactional = transactional

    async def __call__(
        self,
        mongo_resource: Annotated[AsyncMongoResource, Depends(get_mongo_resource)],
        context_provider: Annotated[ContextProviderType, Depends(get_context_provider)],
    ) -> AsyncIterator[Domain]:
        async with BaseDomain(
            resource=mongo_resource,
            context_provider=context_provider,
            transactional=self._transactional,
        ) as domain:
            yield domain
