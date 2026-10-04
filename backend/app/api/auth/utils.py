from typing import Any

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from app.core.settings import Settings
from app.domain.users.entities import UserSession


def make_not_authenticated_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer, Cookie"},
    )


def build_response_with_cookies(
    settings: Settings,
    content: Any,  # noqa: ANN401
    session: UserSession,
) -> JSONResponse:
    response = JSONResponse(content=content, status_code=status.HTTP_200_OK)
    response.set_cookie(
        key="access_token",
        value=session.access_token,
        max_age=settings.access_token_expire,
        secure=settings.cookie_secure,
        httponly=True,
        samesite="strict",
    )
    response.set_cookie(
        key="refresh_token",
        value=session.refresh_token,
        max_age=settings.refresh_token_expire,
        path="/api/auth",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="strict",
    )
    return response
