"""Canonical serialization for financial contracts."""

import hashlib
import json
from dataclasses import asdict, is_dataclass
from decimal import Decimal

from cripto_core.numeric import text


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def record(value: object) -> object:
    if isinstance(value, Decimal):
        return text(value)
    if is_dataclass(value) and not isinstance(value, type):
        return record(asdict(value))
    if isinstance(value, dict):
        return {key: record(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [record(item) for item in value]
    return value


def fingerprint(value: object) -> str:
    return digest(canonical(record(value)).encode())
