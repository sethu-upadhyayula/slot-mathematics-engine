import random
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

from engine.evaluator import evaluate_scatter, evaluate_spin
from engine.models import Grid, WinLine
from engine.slot_machine import SlotMachine

DEFAULT_MULTIPLIER_PROGRESSION = [1, 2, 3, 5]
MAX_CASCADES = 20  # safety cap; a real win/refill cycle should never approach this


@dataclass
class CascadeStep:
    grid: Grid
    win_lines: List[WinLine]
    base_payout: float
    multiplier: float
    payout: float


@dataclass
class CascadeResult:
    initial_grid: Grid
    steps: List[CascadeStep]
    scatter_payout: float
    total_payout: float

    @property
    def num_cascades(self) -> int:
        return len(self.steps)


def _remove_and_refill(
    grid: Grid,
    positions_to_remove: Set[Tuple[int, int]],
    machine: SlotMachine,
    rng: random.Random,
) -> Grid:
    """Winning symbols disappear; remaining symbols keep their relative order
    and drop toward the bottom; new symbols refill from the top, drawn from
    that reel's own symbol distribution (its strip, sampled independently
    rather than read as a continuous window)."""
    marked = [list(column) for column in grid]
    for reel_idx, row_idx in positions_to_remove:
        marked[reel_idx][row_idx] = None

    result = []
    for reel_idx, column in enumerate(marked):
        remaining = [symbol for symbol in column if symbol is not None]
        missing = len(column) - len(remaining)
        reel_symbols = machine.reel_set.reels[reel_idx].symbols
        new_symbols = [rng.choice(reel_symbols) for _ in range(missing)]
        result.append(new_symbols + remaining)
    return result


def run_cascade(
    machine: SlotMachine,
    bet: float = 1.0,
    rng: Optional[random.Random] = None,
    multiplier_progression: Optional[List[float]] = None,
) -> CascadeResult:
    """Spin once, then repeatedly remove winning symbols, drop the rest down,
    refill from the top, and re-evaluate the same paylines, the
    'tumble'/'avalanche' mechanic. The multiplier typically increases with
    each successive cascade to reward longer chains."""
    rng = rng or random.Random()
    progression = multiplier_progression or DEFAULT_MULTIPLIER_PROGRESSION

    initial_grid = machine.reel_set.spin(rng)
    scatter_payout = evaluate_scatter(initial_grid, machine.paytable, bet)

    grid = initial_grid
    steps: List[CascadeStep] = []
    total_payout = scatter_payout

    for cascade_index in range(MAX_CASCADES):
        result = evaluate_spin(grid, machine.paylines, machine.paytable, bet)
        if not result.win_lines:
            break

        multiplier = progression[min(cascade_index, len(progression) - 1)]
        step_payout = result.total_payout * multiplier
        steps.append(
            CascadeStep(
                grid=grid,
                win_lines=result.win_lines,
                base_payout=result.total_payout,
                multiplier=multiplier,
                payout=step_payout,
            )
        )
        total_payout += step_payout

        positions_to_remove = {pos for win in result.win_lines for pos in win.positions}
        grid = _remove_and_refill(grid, positions_to_remove, machine, rng)

    return CascadeResult(
        initial_grid=initial_grid,
        steps=steps,
        scatter_payout=scatter_payout,
        total_payout=total_payout,
    )
