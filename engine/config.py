import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from engine.models import Payline
from engine.paytable import Paytable
from engine.reels import ReelSet, ReelStrip
from engine.slot_machine import SlotMachine
from engine.symbols import Symbol


def load_game_config(path: str) -> SlotMachine:
    data = json.loads(Path(path).read_text())

    reels = [ReelStrip([Symbol(s) for s in reel]) for reel in data["reels"]]
    reel_set = ReelSet(reels, num_rows=data["num_rows"])

    payouts = {}
    for symbol_name, tiers in data["paytable"].items():
        symbol = Symbol(symbol_name)
        for count_str, multiplier in tiers.items():
            payouts[(symbol, int(count_str))] = multiplier

    scatter_payouts = {int(count): value for count, value in data["scatter_paytable"].items()}
    paytable = Paytable(payouts, scatter_payouts)

    paylines = data["paylines"]

    return SlotMachine(reel_set, paylines, paytable)


def machine_to_game_config(machine: SlotMachine, description: str = "") -> Dict[str, Any]:
    """Inverse of load_game_config: serialize a SlotMachine back into the
    same JSON shape, e.g. to save an auto-tuned machine as a reusable config."""
    paytable_json: Dict[str, Dict[str, float]] = {}
    for (symbol, count), multiplier in machine.paytable.payouts.items():
        paytable_json.setdefault(symbol.value, {})[str(count)] = round(multiplier, 4)

    scatter_paytable_json = {
        str(count): round(multiplier, 4) for count, multiplier in machine.paytable.scatter_payouts.items()
    }

    config: Dict[str, Any] = {
        "num_rows": machine.reel_set.num_rows,
        "reels": [[symbol.value for symbol in reel.symbols] for reel in machine.reel_set.reels],
        "paylines": machine.paylines,
        "paytable": paytable_json,
        "scatter_paytable": scatter_paytable_json,
    }
    if description:
        config = {"_description": description, **config}
    return config


def load_template_paytable(
    path: str,
) -> Tuple[List[Payline], Dict[Tuple[Symbol, int], float], Dict[int, float]]:
    """Load just the paylines and paytable "shape" from a config, without
    building a machine, used by tools (the optimizer, the designer
    dashboard) that hold the paytable ratios fixed and vary reel
    composition and/or an overall payout scale instead."""
    data = json.loads(Path(path).read_text())

    paylines = data["paylines"]
    template_paytable = {
        (Symbol(symbol_name), int(count_str)): multiplier
        for symbol_name, tiers in data["paytable"].items()
        for count_str, multiplier in tiers.items()
    }
    template_scatter_paytable = {int(count): value for count, value in data["scatter_paytable"].items()}

    return paylines, template_paytable, template_scatter_paytable
