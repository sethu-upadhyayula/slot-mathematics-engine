import math
import random
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from engine.slot_machine import SlotMachine
from engine.symbols import Symbol
from scipy import stats

Z_95 = float(stats.norm.ppf(0.975))


@dataclass
class StreamingStats:
    """Running statistics computed one spin at a time via Welford's
    online algorithm, O(1) memory regardless of how many spins are
    processed, unlike SpinBatch (simulation/simulate.py), which stores
    every payout and therefore uses memory proportional to N. This is
    what makes 10M+ spin runs practical: at 100M spins, a Python list of
    payouts alone would cost several GB; this accumulator costs a few
    hundred bytes no matter how many spins it's seen.
    """

    bet: float = 1.0
    num_spins: int = 0
    mean: float = 0.0
    _m2: float = 0.0
    hits: int = 0
    scatter_triggers: int = 0
    max_payout: float = 0.0
    symbol_counts: Dict[Symbol, int] = field(default_factory=dict)

    def update(self, payout: float, scatter_count: int, scatter_trigger_threshold: int = 3) -> None:
        self.num_spins += 1
        delta = payout - self.mean
        self.mean += delta / self.num_spins
        delta2 = payout - self.mean
        self._m2 += delta * delta2

        if payout > 0:
            self.hits += 1
        if scatter_count >= scatter_trigger_threshold:
            self.scatter_triggers += 1
        if payout > self.max_payout:
            self.max_payout = payout

    def update_symbol_counts(self, grid) -> None:
        for column in grid:
            for symbol in column:
                self.symbol_counts[symbol] = self.symbol_counts.get(symbol, 0) + 1

    @property
    def variance(self) -> float:
        return self._m2 / self.num_spins if self.num_spins else 0.0

    @property
    def std_dev(self) -> float:
        return math.sqrt(self.variance)

    @property
    def rtp(self) -> float:
        return self.mean / self.bet if self.bet else 0.0

    @property
    def hit_frequency(self) -> float:
        return self.hits / self.num_spins if self.num_spins else 0.0

    @property
    def scatter_trigger_frequency(self) -> float:
        return self.scatter_triggers / self.num_spins if self.num_spins else 0.0

    @property
    def max_win_multiplier(self) -> float:
        return self.max_payout / self.bet if self.bet else 0.0

    @property
    def standard_error(self) -> float:
        return self.std_dev / math.sqrt(self.num_spins) if self.num_spins else 0.0

    @property
    def confidence_interval_95(self) -> Tuple[float, float]:
        se = self.standard_error / self.bet
        return (self.rtp - Z_95 * se, self.rtp + Z_95 * se)


def run_spins_streaming(
    machine: SlotMachine,
    num_spins: int,
    bet: float = 1.0,
    rng: Optional[random.Random] = None,
    track_symbol_counts: bool = True,
    scatter_trigger_threshold: int = 3,
) -> StreamingStats:
    rng = rng or random.Random()
    accumulator = StreamingStats(bet=bet)

    for _ in range(num_spins):
        result = machine.spin(bet=bet, rng=rng)
        scatter_count = sum(column.count(Symbol.SCATTER) for column in result.grid)
        accumulator.update(result.total_payout, scatter_count, scatter_trigger_threshold)
        if track_symbol_counts:
            accumulator.update_symbol_counts(result.grid)

    return accumulator
