from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.dependencies import get_templates
from app.api.errors import AuthorizationError
from app.api.logger import logger
from app.core.settings import Settings
from app.domain.exceptions import (
    BadRequestError,
    ConflictError,
    DomainError,
    ForbiddenError,
    NotFoundError,
    UnprocessableContentError,
)

ERROR_MAPPING: dict[type[DomainError], int] = {
    BadRequestError: status.HTTP_400_BAD_REQUEST,
    ForbiddenError: status.HTTP_403_FORBIDDEN,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    UnprocessableContentError: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


def add_exception_handlers(app: FastAPI, settings: Settings) -> None:
    templates = get_templates(settings=settings)

    @app.exception_handler(DomainError)
    async def domain_exception_handler(
        request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        for error_cls in type(exc).mro():
            if issubclass(error_cls, DomainError) and error_cls in ERROR_MAPPING:
                status_code = ERROR_MAPPING[error_cls]
                break

        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> Response:
        exc_name = exc.__class__.__name__
        message = f"{request.method} {request.url.path} - {exc_name}: {exc}"
        logger.warning(message)
        if "text/html" in request.headers.get("accept", ""):
            return templates.TemplateResponse(request=request, name="error.html")

        return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})

    @app.exception_handler(AuthorizationError)
    async def authorization_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> Response:
        exc_name = exc.__class__.__name__
        message = f"{request.method} {request.url.path} - {exc_name}: {exc}"
        logger.warning(message)
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
