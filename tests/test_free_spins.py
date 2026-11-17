import random

from engine.features.free_spins import (
    FreeSpinsConfig,
    _apply_sticky_wilds,
    count_scatters,
    play_round,
    run_free_spins,
)
from engine.paytable import Paytable
from engine.reels import ReelSet, ReelStrip
from engine.slot_machine import SlotMachine
from engine.symbols import Symbol


def test_count_scatters():
    grid = [
        [Symbol.SCATTER, Symbol.CHERRY],
        [Symbol.SCATTER, Symbol.SCATTER],
    ]
    assert count_scatters(grid) == 3


def test_apply_sticky_wilds_forces_positions_to_wild():
    grid = [
        [Symbol.CHERRY, Symbol.LEMON],
        [Symbol.ORANGE, Symbol.PLUM],
    ]
    sticky_positions = {(0, 1), (1, 0)}

    new_grid = _apply_sticky_wilds(grid, sticky_positions)

    assert new_grid == [[Symbol.CHERRY, Symbol.WILD], [Symbol.WILD, Symbol.PLUM]]


def test_play_round_no_bonus_when_scatters_can_never_appear():
    # No SCATTER symbol anywhere in the reel strips, so the trigger can never fire.
    reels = [ReelStrip([Symbol.CHERRY]) for _ in range(3)]
    reel_set = ReelSet(reels, num_rows=1)
    paytable = Paytable(payouts={(Symbol.CHERRY, 3): 5}, scatter_payouts={})
    machine = SlotMachine(reel_set, paylines=[[0, 0, 0]], paytable=paytable)
    config = FreeSpinsConfig(trigger_scatter_count=3, spins_awarded=10)

    result = play_round(machine, config, bet=1.0, rng=random.Random(0))

    assert result.free_spins is None
    assert result.total_payout == result.base_spin.total_payout


def test_play_round_triggers_bonus_when_scatters_meet_threshold():
    # Every reel is always SCATTER, so the base spin always meets the trigger.
    reels = [ReelStrip([Symbol.SCATTER]) for _ in range(3)]
    reel_set = ReelSet(reels, num_rows=1)
    paytable = Paytable(payouts={}, scatter_payouts={3: 2})
    machine = SlotMachine(reel_set, paylines=[], paytable=paytable)
    # retrigger_spins_awarded=0 keeps this finite even though every spin re-triggers:
    # each iteration still consumes exactly one spin from the counter.
    config = FreeSpinsConfig(
        trigger_scatter_count=3, spins_awarded=2, retrigger_scatter_count=3, retrigger_spins_awarded=0
    )

    result = play_round(machine, config, bet=1.0, rng=random.Random(0))

    assert result.free_spins is not None
    assert result.free_spins.spins_played == 2
    assert result.free_spins.retriggers == 2  # every spin re-triggers, just doesn't extend the round


def test_run_free_spins_bookkeeping_is_internally_consistent():
    # Reel mostly non-scatter, occasionally scatter, realistic-ish odds, no infinite loop risk
    # because retrigger_spins_awarded is small relative to how rare the retrigger condition is.
    symbols = [Symbol.CHERRY] * 18 + [Symbol.SCATTER] * 2
    reels = [ReelStrip(list(symbols)) for _ in range(3)]
    reel_set = ReelSet(reels, num_rows=1)
    paytable = Paytable(payouts={(Symbol.CHERRY, 3): 5}, scatter_payouts={})
    machine = SlotMachine(reel_set, paylines=[[0, 0, 0]], paytable=paytable)
    config = FreeSpinsConfig(
        trigger_scatter_count=3, spins_awarded=20, retrigger_scatter_count=3, retrigger_spins_awarded=5
    )

    result = run_free_spins(machine, config, bet=1.0, rng=random.Random(42))

    assert result.spins_played == 20 + result.retriggers * 5
    assert sum(r.total_payout for r in result.spin_results) == result.total_payout
