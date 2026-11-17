import random

from engine.features.cascade import _remove_and_refill, run_cascade
from engine.paytable import Paytable
from engine.reels import ReelSet, ReelStrip
from engine.slot_machine import SlotMachine
from engine.symbols import Symbol


def test_remove_and_refill_drops_remaining_symbols_and_fills_from_top():
    grid = [
        [Symbol.CHERRY, Symbol.LEMON, Symbol.PLUM],  # reel 0, row 0 removed
        [Symbol.ORANGE, Symbol.BAR, Symbol.SEVEN],  # reel 1, row 1 removed
    ]
    # Deterministic single-symbol strips so the refill symbol is known exactly.
    reels = [ReelStrip([Symbol.WILD]), ReelStrip([Symbol.SCATTER])]
    reel_set = ReelSet(reels, num_rows=3)
    machine = SlotMachine(reel_set, paylines=[[0, 0]], paytable=Paytable({}, {}))

    positions_to_remove = {(0, 0), (1, 1)}
    new_grid = _remove_and_refill(grid, positions_to_remove, machine, random.Random(1))

    # Reel 0: removing the top symbol leaves the rest untouched; new symbol fills the gap at the top.
    assert new_grid[0] == [Symbol.WILD, Symbol.LEMON, Symbol.PLUM]
    # Reel 1: removing the middle symbol drops ORANGE down one row; new symbol fills the top.
    assert new_grid[1] == [Symbol.SCATTER, Symbol.ORANGE, Symbol.SEVEN]


def test_run_cascade_stops_when_no_more_wins():
    # A machine that can never win: every reel is a different, non-matching symbol.
    reels = [ReelStrip([Symbol.CHERRY]), ReelStrip([Symbol.LEMON]), ReelStrip([Symbol.ORANGE])]
    reel_set = ReelSet(reels, num_rows=1)
    machine = SlotMachine(reel_set, paylines=[[0, 0, 0]], paytable=Paytable({}, {}))

    result = run_cascade(machine, bet=1.0, rng=random.Random(0))

    assert result.num_cascades == 0
    assert result.total_payout == 0.0


def test_run_cascade_applies_increasing_multiplier_per_step():
    # Every reel is identical (all CHERRY), so the very first evaluation always
    # wins, and refills are also always CHERRY, so it keeps winning until the
    # safety cap, enough to check the multiplier progression is applied in order.
    reels = [ReelStrip([Symbol.CHERRY]) for _ in range(3)]
    reel_set = ReelSet(reels, num_rows=1)
    paytable = Paytable(payouts={(Symbol.CHERRY, 3): 10}, scatter_payouts={})
    machine = SlotMachine(reel_set, paylines=[[0, 0, 0]], paytable=paytable)

    result = run_cascade(machine, bet=1.0, rng=random.Random(0), multiplier_progression=[1, 2, 3])

    assert result.num_cascades >= 3
    assert [step.multiplier for step in result.steps[:3]] == [1, 2, 3]
    # Progression holds at its last value once exhausted.
    assert result.steps[3].multiplier == 3
