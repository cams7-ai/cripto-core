import copy
import json
from pathlib import Path

PARAMETERS = {"fee_bps": "10", "spread_bps": "10", "slippage_bps": "5", "max_quote_age_ms": 5000}


def scenario():
    return json.loads((Path(__file__).parent / "fixtures/roundtrip.json").read_text())


def context(path):
    return {"parameters": dict(PARAMETERS), "rules": scenario()["rules"]}


def order(index=1, **changes):
    event = copy.deepcopy(scenario()["events"][index])
    event.update(changes)
    event["action_key"] = "paper-demo:roundtrip-v1:" + event["action_id"]
    return event
