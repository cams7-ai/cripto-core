"""Immutable synthetic execution plan; no wallet or persistence."""

from dataclasses import dataclass
from decimal import Decimal

from cripto_core.serialization import fingerprint, record

# Existing plan identity is part of the paper-integral-v1 wire contract.
MODEL = "paper-integral-v1"


@dataclass(frozen=True)
class Plan:
    action: str
    side: str
    requested: Decimal
    quantity: Decimal
    price: Decimal
    notional: Decimal
    fee: Decimal
    mark: Decimal
    fill_at: int
    observed_at: int

    @property
    def asset(self) -> str:
        return "USDT" if self.side == "BUY" else "BTC"

    @property
    def reserve(self) -> Decimal:
        return self.notional + self.fee if self.side == "BUY" else self.quantity

    @property
    def fill_id(self) -> str:
        return fingerprint({"model": MODEL, "plan": record(self)})
