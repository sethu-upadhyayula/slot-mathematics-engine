import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from engine.slot_machine import SlotMachine
from engine.symbols import Symbol


@dataclass
class SpinBatch:
    """Raw output of running many spins, before any statistics are computed."""

    bet: float
    payouts: List[float] = field(default_factory=list)
    scatter_counts: List[int] = field(default_factory=list)
    symbol_counts: Dict[Symbol, int] = field(default_factory=dict)

    @property
    def num_spins(self) -> int:
        return len(self.payouts)


def run_spins(
    machine: SlotMachine,
    num_spins: int,
    bet: float = 1.0,
    rng: Optional[random.Random] = None,
) -> SpinBatch:
    rng = rng or random.Random()
    batch = SpinBatch(bet=bet)

    for _ in range(num_spins):
        result = machine.spin(bet=bet, rng=rng)
        batch.payouts.append(result.total_payout)

        scatter_count = sum(column.count(Symbol.SCATTER) for column in result.grid)
        batch.scatter_counts.append(scatter_count)

        for column in result.grid:
            for symbol in column:
                batch.symbol_counts[symbol] = batch.symbol_counts.get(symbol, 0) + 1

    return batch
