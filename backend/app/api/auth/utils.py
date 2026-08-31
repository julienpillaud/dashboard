from typing import Annotated

from fastapi import Form, HTTPException, status
from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: str


def make_not_authenticated_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


class OAuth2RefreshTokenRequestForm:
    def __init__(
        self,
        *,
        grant_type: Annotated[str, Form(pattern="^refresh_token$")],
        refresh_token: Annotated[str, Form()],
        scope: Annotated[str, Form()] = "",
    ) -> None:
        self.grant_type = grant_type
        self.refresh_token = refresh_token
        self.scopes = scope.split()
