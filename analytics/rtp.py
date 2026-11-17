import itertools
import random
from typing import Iterator, Optional

from engine.evaluator import evaluate_spin
from engine.models import Grid
from engine.slot_machine import SlotMachine


def total_combinations(machine: SlotMachine) -> int:
    total = 1
    for reel in machine.reel_set.reels:
        total *= reel.length
    return total


def _iter_all_grids(machine: SlotMachine) -> Iterator[Grid]:
    reel_lengths = [reel.length for reel in machine.reel_set.reels]
    for stops in itertools.product(*(range(length) for length in reel_lengths)):
        yield machine.reel_set.grid_from_stops(stops)


def exact_rtp(machine: SlotMachine, bet: float = 1.0) -> float:
    """Exact RTP via exhaustive enumeration of every reel-stop combination.

    Each combination is equally likely, so RTP is just the average payout
    across all of them. Only feasible while total_combinations(machine)
    stays in the low millions or below.
    """
    total_payout = 0.0
    count = 0

    for grid in _iter_all_grids(machine):
        result = evaluate_spin(grid, machine.paylines, machine.paytable, bet)
        total_payout += result.total_payout
        count += 1

    return total_payout / (count * bet)


def monte_carlo_rtp(
    machine: SlotMachine,
    num_spins: int,
    bet: float = 1.0,
    rng: Optional[random.Random] = None,
) -> float:
    """Estimate RTP by sampling spins instead of enumerating every outcome.

    This is the approach real games use in practice, since actual reel
    strips are far too long to enumerate exhaustively.
    """
    rng = rng or random.Random()
    total_payout = 0.0

    for _ in range(num_spins):
        result = machine.spin(bet=bet, rng=rng)
        total_payout += result.total_payout

    return total_payout / (num_spins * bet)
