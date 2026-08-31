from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.core.logger import logger
from app.domain.exceptions import (
    BadRequestError,
    ConflictError,
    DomainError,
    NotFoundError,
    UnprocessableContentError,
)


class APIError(Exception):
    def __init__(self, message: str) -> None:
        logger.error(message)
        super().__init__(message)


class SecurityError(APIError):
    pass


class InvalidAccessTokenError(SecurityError):
    pass


ERROR_MAPPING: dict[type[DomainError], int] = {
    BadRequestError: status.HTTP_400_BAD_REQUEST,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    UnprocessableContentError: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


def add_exception_handlers(app: FastAPI) -> None:
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
