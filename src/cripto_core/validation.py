"""Small shared validation and explicit UTC timestamps."""

import re
from datetime import UTC, datetime
from typing import cast

from cripto_core.errors import MarketError, PaperError

EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(k, str) for k in value):
        raise MarketError("INVALID_OBJECT")
    return cast(dict[str, object], value)


def sequence(value: object) -> list[object]:
    if not isinstance(value, list):
        raise MarketError("INVALID_ARRAY")
    return cast(list[object], value)


def identifier(value: object) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9_-]{1,64}", value) is None:
        raise PaperError("INVALID_ID")
    return value


def instant(value: object) -> int:
    if not isinstance(value, str):
        raise PaperError("INVALID_TIME")
    try:
        dt = datetime.fromisoformat(value)
        if dt.utcoffset() is None:
            raise ValueError
        delta = dt.astimezone(UTC) - EPOCH
        result = delta.days * 86400000 + delta.seconds * 1000 + delta.microseconds // 1000
        if result < 0 or delta.microseconds % 1000:
            raise ValueError
        return result
    except (ValueError, OverflowError):
        raise PaperError("INVALID_TIME") from None


def require_object(value: object) -> dict[str, object]:
    try:
        return mapping(value)
    except ValueError:
        raise PaperError("INVALID_PAYLOAD") from None
