import datetime
import hashlib
import uuid

import jwt
from cleanstack import EntityId
from pwdlib import PasswordHash

from app.core.settings import Settings
from app.domain.refresh_tokens.entities import RefreshToken

password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


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
        key=settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


def generate_refresh_token(
    settings: Settings,
    raw_value: str,
    user_id: EntityId,
    current_date: datetime.datetime | None = None,
) -> RefreshToken:
    current_date = current_date or datetime.datetime.now(datetime.UTC)
    delta = datetime.timedelta(seconds=settings.refresh_token_expire)
    return RefreshToken(
        id=uuid.uuid7(),
        hash_value=hash_refresh_token(raw_value),
        user_id=user_id,
        created_at=current_date,
        expires_at=current_date + delta,
    )


def hash_refresh_token(value: str, /) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
