"""Explicit Decimal conversion and original monetary rounding."""

import re
from decimal import ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN, Decimal, InvalidOperation

from cripto_core.errors import PaperError

Q = Decimal("0.00000001")
ZERO = Decimal("0")


def parse_decimal(value: object) -> Decimal:
    """Aceita exclusivamente texto decimal finito, sem conversao por float."""
    if not isinstance(value, str):
        raise ValueError("decimal exige string")
    try:
        result = Decimal(value)
    except InvalidOperation:
        raise ValueError("decimal invalido") from None
    if not result.is_finite():
        raise ValueError("decimal deve ser finito")
    return result


def number(value: object, *, signed: bool = False) -> Decimal:
    pattern = r"-?[0-9]{1,18}(?:\.[0-9]{1,8})?" if signed else r"[0-9]{1,18}(?:\.[0-9]{1,8})?"
    if not isinstance(value, str) or re.fullmatch(pattern, value) is None:
        raise PaperError("INVALID_DECIMAL")
    return Decimal(value)


def text(value: Decimal) -> str:
    result = format(value.quantize(Q, rounding=ROUND_HALF_EVEN), "f")
    number(result, signed=True)
    return result


def bounded(value: Decimal) -> Decimal:
    if value != value.quantize(Q) or abs(value) >= Decimal("1000000000000000000"):
        raise PaperError("DECIMAL_RANGE")
    return value


def money(value: Decimal, *, up: bool = False) -> Decimal:
    return bounded(value.quantize(Q, rounding=ROUND_CEILING if up else ROUND_FLOOR))
