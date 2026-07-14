from collections.abc import AsyncIterator, Callable
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from app.core.context import ContextProvider
from app.core.domain import Domain, DomainManager, ResourceProtocol
from app.core.logger import logger
from app.core.settings import Settings
from app.domain.context import ContextProtocol
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
    mongo_client = request.app.state.mongo_client
    return AsyncMongoResource(mongo_client)


def get_context_provider(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> Callable[[ResourceProtocol], ContextProtocol]:
    return ContextProvider(
        settings=settings,
        http_client=request.app.state.http_client,
    )


class DomainProvider:
    def __init__(
        self,
        transactional: bool = False,
        scope: str = "domain",
    ) -> None:
        self._transactional = transactional
        self._scope = scope

    async def __call__(
        self,
        request: Request,
        mongo_resource: Annotated[AsyncMongoResource, Depends(get_mongo_resource)],
        context_provider: Annotated[
            Callable[[ResourceProtocol], ContextProtocol],
            Depends(get_context_provider),
        ],
    ) -> AsyncIterator[Domain]:
        logger.debug(f"Domain '{self._scope}' transactional={self._transactional}")
        if not hasattr(request.state, "domains_cache"):
            request.state.domains_cache = {}

        existing_domain = request.state.domains_cache.get(self._scope)
        if existing_domain is not None:
            yield existing_domain
            return

        async with DomainManager(
            resource=mongo_resource,
            context_provider=context_provider,
            transactional=self._transactional,
        ) as domain:
            request.state.domains_cache[self._scope] = domain

            try:
                yield domain
            finally:
                request.state.domains_cache.pop(self._scope, None)


get_auth_domain = DomainProvider(transactional=False, scope="auth")
