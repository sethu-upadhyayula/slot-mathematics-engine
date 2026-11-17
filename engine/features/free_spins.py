import random
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

from engine.evaluator import evaluate_spin
from engine.models import Grid, SpinResult
from engine.slot_machine import SlotMachine
from engine.symbols import Symbol


@dataclass
class FreeSpinsConfig:
    trigger_scatter_count: int = 3
    spins_awarded: int = 10
    retrigger_scatter_count: int = 3
    retrigger_spins_awarded: int = 5
    sticky_wilds: bool = False


@dataclass
class FreeSpinsResult:
    spin_results: List[SpinResult] = field(default_factory=list)
    total_payout: float = 0.0
    spins_played: int = 0
    retriggers: int = 0


@dataclass
class RoundResult:
    base_spin: SpinResult
    free_spins: Optional[FreeSpinsResult]
    total_payout: float


def count_scatters(grid: Grid) -> int:
    return sum(column.count(Symbol.SCATTER) for column in grid)


def _apply_sticky_wilds(grid: Grid, sticky_positions: Set[Tuple[int, int]]) -> Grid:
    new_grid = [list(column) for column in grid]
    for reel_idx, row_idx in sticky_positions:
        new_grid[reel_idx][row_idx] = Symbol.WILD
    return new_grid


def run_free_spins(
    machine: SlotMachine,
    config: FreeSpinsConfig,
    bet: float = 1.0,
    rng: Optional[random.Random] = None,
) -> FreeSpinsResult:
    """Play out a free spins round, including retriggers and (optionally)
    sticky wilds that accumulate and persist for the rest of the round.

    Note: for the round to have a finite expected length, the expected
    extra spins per spin played (retrigger probability x
    retrigger_spins_awarded) must stay below 1 - the same extinction
    condition that governs a branching process.
    """
    rng = rng or random.Random()

    spins_remaining = config.spins_awarded
    spins_played = 0
    retriggers = 0
    total_payout = 0.0
    spin_results: List[SpinResult] = []
    sticky_positions: Set[Tuple[int, int]] = set()

    while spins_remaining > 0:
        grid = machine.reel_set.spin(rng)

        if config.sticky_wilds:
            grid = _apply_sticky_wilds(grid, sticky_positions)
            for reel_idx, column in enumerate(grid):
                for row_idx, symbol in enumerate(column):
                    if symbol == Symbol.WILD:
                        sticky_positions.add((reel_idx, row_idx))

        result = evaluate_spin(grid, machine.paylines, machine.paytable, bet)
        spin_results.append(result)
        total_payout += result.total_payout
        spins_played += 1
        spins_remaining -= 1

        if count_scatters(grid) >= config.retrigger_scatter_count:
            spins_remaining += config.retrigger_spins_awarded
            retriggers += 1

    return FreeSpinsResult(
        spin_results=spin_results,
        total_payout=total_payout,
        spins_played=spins_played,
        retriggers=retriggers,
    )


def play_round(
    machine: SlotMachine,
    config: FreeSpinsConfig,
    bet: float = 1.0,
    rng: Optional[random.Random] = None,
) -> RoundResult:
    """Play one base-game spin; if it lands enough scatters, play the
    resulting free spins round too. This is the entry point later analysis
    code should use in place of machine.spin() once free spins are in play,
    since the bonus round changes the true per-spin RTP."""
    rng = rng or random.Random()

    base_result = machine.spin(bet=bet, rng=rng)
    total_payout = base_result.total_payout
    free_spins_result = None

    if count_scatters(base_result.grid) >= config.trigger_scatter_count:
        free_spins_result = run_free_spins(machine, config, bet=bet, rng=rng)
        total_payout += free_spins_result.total_payout

    return RoundResult(base_spin=base_result, free_spins=free_spins_result, total_payout=total_payout)
