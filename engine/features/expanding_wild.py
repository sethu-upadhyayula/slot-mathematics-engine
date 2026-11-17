from engine.evaluator import evaluate_spin
from engine.models import Grid, SpinResult
from engine.slot_machine import SlotMachine
from engine.symbols import Symbol


def apply_expanding_wilds(grid: Grid) -> Grid:
    """Any reel containing at least one Wild becomes entirely Wild for this spin."""
    expanded = []
    for column in grid:
        if Symbol.WILD in column:
            expanded.append([Symbol.WILD] * len(column))
        else:
            expanded.append(list(column))
    return expanded


def spin_with_expanding_wilds(machine: SlotMachine, bet: float = 1.0, rng=None) -> SpinResult:
    grid = machine.reel_set.spin(rng)
    expanded_grid = apply_expanding_wilds(grid)
    return evaluate_spin(expanded_grid, machine.paylines, machine.paytable, bet)
