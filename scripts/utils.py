from decimal import Decimal
from functools import lru_cache
from typing import Any

import httpx
from pydantic import PositiveFloat

from app.domain.articles.entities import (
    ArticleDeposit,
    ArticleOrigin,
    ArticleVolume,
    VolumeUnit,
)


def empty_to_none(value: Any) -> Any | None:  # noqa: ANN401
    return value or None


def convert_volume(value: float, unit: str) -> tuple[PositiveFloat, VolumeUnit]:
    if unit == VolumeUnit.CENTILITER and value >= 100:  # noqa: PLR2004
        value /= 100
        unit = VolumeUnit.LITER
    return value, VolumeUnit(unit)


def get_volume(article: dict[str, Any]) -> ArticleVolume | None:
    volume = article["volume"]
    if not volume:
        return None

    value, unit = convert_volume(
        value=volume["value"],
        unit=volume["unit"],
    )
    return ArticleVolume(value=value, unit=unit)


def get_deposit(article: dict[str, Any]) -> ArticleDeposit | None:
    unit = article["deposit"]["unit"]
    if not unit:
        return None

    return ArticleDeposit(
        unit=unit,
        crate=article["deposit"]["case"] or None,
        packaging=article["packaging"] or None,
    )


@lru_cache
def fetch_codes() -> dict[str, str]:
    response = httpx.get("https://flagcdn.com/fr/codes.json")
    return {v: k for k, v in response.json().items()}


def get_origin(value: Any) -> ArticleOrigin | None:  # noqa: ANN401
    if not value:
        return None

    codes = fetch_codes()
    code = codes.get(value)
    return ArticleOrigin(name=value, code=code)


def to_decimal(value: float) -> Decimal:
    return Decimal(str(value))


def get_total_cost(article: dict[str, Any]) -> Decimal:
    return (
        to_decimal(article["buy_price"])
        + to_decimal(article["excise_duty"])
        + to_decimal(article["social_security_levy"])
    )
