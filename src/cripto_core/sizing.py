"""Original sizing arithmetic with explicit balances, no wallet access."""

from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from math import lcm

from cripto_core.errors import PaperError
from cripto_core.execution import filters, observation
from cripto_core.numeric import Q, number


def sized_quantity(
    usdt_free: Decimal,
    equity: Decimal,
    module: dict[str, object],
    quote: dict[str, object],
    at: int,
    parameters: dict[str, object],
    rules: dict[str, object],
) -> Decimal:
    _, mark = observation(quote, at, int(str(parameters["max_quote_age_ms"])))
    supplied = filters(rules)
    # Mesmo modelo de preco da 03; make_plan/admit revalidam o plano definitivo.
    slip = number(parameters["slippage_bps"]) / 10000
    price = (
        mark * (1 + number(parameters["spread_bps"]) / 20000 + slip)
        if quote["kind"] == "REFERENCE"
        else number(quote["ask"]) * (1 + slip)
    )
    tick = number(supplied["PRICE_FILTER"]["tickSize"]) or Q
    price = (price / tick).to_integral_value(rounding=ROUND_CEILING) * tick
    if price <= 0:
        raise PaperError("INVALID_PRICE")
    budget = min(
        usdt_free,
        equity * number(module["capital_weight"]),
        equity * number(parameters["max_entry_fraction"]),
        equity * number(parameters["max_exposure_fraction"]),
    )
    step_units = [
        int(number(supplied[name]["stepSize"]) / Q)
        for name in ("LOT_SIZE", "MARKET_LOT_SIZE")
        if number(supplied[name]["stepSize"])
    ]
    step = Decimal(lcm(*step_units)) * Q if step_units else Q
    return (
        budget / (price * (1 + number(parameters["fee_bps"]) / 10000)) / step
    ).to_integral_value(rounding=ROUND_FLOOR) * step
