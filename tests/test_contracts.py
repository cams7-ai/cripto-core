import ast
import importlib.util
import subprocess
import sys
from decimal import Decimal, localcontext
from pathlib import Path

import pytest

from cripto_core.errors import PaperError
from cripto_core.numeric import bounded, money, number, parse_decimal, text
from cripto_core.serialization import canonical, fingerprint, record
from cripto_core.sizing import sized_quantity
from cripto_core.validation import identifier, instant, require_object
from tests.helpers import context, order


@pytest.mark.parametrize("value", [0.1, True, None, "NaN", "Infinity", "-Infinity", "bad"])
def test_finite_text_conversion(value):
    with pytest.raises(ValueError):
        parse_decimal(value)


@pytest.mark.parametrize("value", [0.1, True, "1e1", "NaN", "Infinity", "-1", "1.000000001"])
def test_money_input_rejects_invalid_forms(value):
    with pytest.raises(PaperError):
        number(value)


def test_independent_decimal_and_rounding_oracles():
    assert parse_decimal("0.1") + parse_decimal("0.2") == Decimal("0.3")
    assert money(Decimal("1.000000001")) == Decimal("1.00000000")
    assert money(Decimal("1.000000001"), up=True) == Decimal("1.00000001")
    assert text(Decimal("1.234567885")) == "1.23456788"
    assert text(Decimal("1.234567895")) == "1.23456790"
    with pytest.raises(PaperError, match="DECIMAL_RANGE"):
        bounded(Decimal("1.000000001"))
    assert fingerprint({"b": Decimal("0.2"), "a": Decimal("0.1")}) == fingerprint(
        {"a": "0.10000000", "b": "0.20000000"}
    )
    assert record((Decimal("1"),)) == ["1.00000000"]
    with pytest.raises(ValueError):
        canonical(float("nan"))


def test_explicit_time_payload_validation():
    assert instant("1970-01-01T00:00:00.001Z") == 1
    for value in [None, "2026-01-01", "1969-12-31T23:59:59Z", "1970-01-01T00:00:00.0001Z"]:
        with pytest.raises(PaperError):
            instant(value)
    with pytest.raises(PaperError):
        require_object([])
    with pytest.raises(PaperError):
        identifier("../bad")


def test_sizing_uses_explicit_budget_without_a_wallet(tmp_path):
    ctx = context(tmp_path)
    event = order()
    params = {**ctx["parameters"], "max_entry_fraction": "0.10", "max_exposure_fraction": "0.10"}
    with localcontext() as lc:
        lc.prec = 80
        result = sized_quantity(
            Decimal("10000"),
            Decimal("10000"),
            {"capital_weight": "0.10"},
            event["observation"],
            instant(event["fill_at"]),
            params,
            ctx["rules"],
        )
    assert result == Decimal("9.980029")


def test_all_transitive_runtime_imports_are_pure_and_core_only():
    package = Path(importlib.util.find_spec("cripto_core").origin).parent
    allowed = {
        "__future__",
        "dataclasses",
        "decimal",
        "typing",
        "datetime",
        "math",
        "re",
        "json",
        "hashlib",
        "cripto_core",
    }
    for source in package.rglob("*.py"):
        for node in ast.walk(ast.parse(source.read_text())):
            if isinstance(node, ast.Import):
                assert all(n.name.split(".")[0] in allowed for n in node.names), source
            elif isinstance(node, ast.ImportFrom):
                assert node.module.split(".")[0] in allowed, source
    assert importlib.util.find_spec("cripto_bot") is None


def test_import_does_not_change_global_decimal_context():
    code = (
        "from decimal import getcontext; c=getcontext().copy(); "
        "import cripto_core.execution, cripto_core.sizing, cripto_core.strategy.sma; "
        "assert getcontext()==c"
    )
    # Context does not implement structural equality; compare its explicit representation.
    code = code.replace("getcontext()==c", "str(getcontext())==str(c)")
    proc = subprocess.run([sys.executable, "-I", "-c", code], text=True, capture_output=True)
    assert proc.returncode == 0, proc.stderr
