import datetime
import uuid
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import APIKeyCookie
from pydantic import BaseModel, ValidationError

from app.api.auth.utils import make_not_authenticated_error
from app.api.dependencies.app import get_settings
from app.api.exceptions import InvalidAccessTokenError
from app.core.settings import Settings

cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)


class TokenPayload(BaseModel):
    sub: uuid.UUID
    exp: datetime.datetime
    iat: datetime.datetime


def decode_access_token(settings: Settings, value: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            jwt=value,
            key=settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError as error:
        raise InvalidAccessTokenError("Token expired") from error
    except jwt.PyJWTError as error:
        raise InvalidAccessTokenError("Could not decode token") from error

    try:
        return TokenPayload.model_validate(payload)
    except ValidationError as error:
        raise InvalidAccessTokenError("Invalid token payload") from error


def get_current_user_id(
    settings: Annotated[Settings, Depends(get_settings)],
    access_token: Annotated[str | None, Depends(cookie_scheme)],
) -> uuid.UUID:
    if not access_token:
        raise make_not_authenticated_error()

    try:
        access_payload = decode_access_token(settings=settings, value=access_token)
    except InvalidAccessTokenError as error:
        raise make_not_authenticated_error() from error

    return access_payload.sub
