import datetime
import uuid

import jwt
from cleanstack import EntityId
from pydantic import BaseModel, ValidationError

from app.api.errors import InvalidAccessToken
from app.core.settings import Settings


class TokenPayload(BaseModel):
    sub: uuid.UUID
    exp: datetime.datetime
    iat: datetime.datetime


def generate_access_token(
    settings: Settings,
    user_id: EntityId,
    current_date: datetime.datetime | None = None,
) -> str:
    current_date = current_date or datetime.datetime.now(datetime.UTC)
    delta = datetime.timedelta(seconds=settings.access_token_expire)
    return jwt.encode(
        payload={
            "sub": str(user_id),
            "exp": current_date + delta,
            "iat": current_date,
        },
        key=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(settings: Settings, value: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            jwt=value,
            key=settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError as error:
        raise InvalidAccessToken("Token expired") from error
    except jwt.PyJWTError as error:
        raise InvalidAccessToken("Could not decode token") from error

    try:
        return TokenPayload.model_validate(payload)
    except ValidationError as error:
        raise InvalidAccessToken("Invalid token payload") from error
