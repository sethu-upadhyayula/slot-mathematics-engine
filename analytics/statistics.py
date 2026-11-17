import math
from dataclasses import dataclass
from typing import Dict, List

from simulation.simulate import SpinBatch

# Win-size buckets, expressed as multiples of bet. Standard way slot
# mathematicians summarize a payout distribution's shape at a glance.
HISTOGRAM_BUCKETS = [
    ("0x (no win)", None, 0),
    ("(0x, 1x]", 0, 1),
    ("(1x, 5x]", 1, 5),
    ("(5x, 20x]", 5, 20),
    ("(20x, 100x]", 20, 100),
    ("100x+", 100, None),
]


@dataclass
class GameStatistics:
    num_spins: int
    bet: float

    rtp: float
    house_edge: float
    mean_payout: float

    variance: float
    std_dev: float
    skewness: float
    kurtosis: float

    hit_frequency: float
    scatter_trigger_frequency: float

    max_win_multiplier: float
    percentiles: Dict[float, float]

    symbol_frequency: Dict[str, float]
    win_histogram: Dict[str, int]

    @property
    def median_win_multiplier(self) -> float:
        return self.percentiles[50]

    @property
    def coefficient_of_variation(self) -> float:
        """Std dev relative to the mean - a scale-free volatility index that
        lets you compare games with different RTPs on the same footing."""
        return self.std_dev / self.rtp if self.rtp else 0.0


def _percentile(sorted_values: List[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    index = min(int(p / 100 * len(sorted_values)), len(sorted_values) - 1)
    return sorted_values[index]


def build_win_histogram(payouts: List[float], bet: float) -> Dict[str, int]:
    buckets = {label: 0 for label, _, _ in HISTOGRAM_BUCKETS}
    for payout in payouts:
        multiplier = payout / bet
        for label, low, high in HISTOGRAM_BUCKETS:
            if low is None:
                if multiplier <= high:
                    buckets[label] += 1
                    break
            elif high is None:
                if multiplier > low:
                    buckets[label] += 1
                    break
            elif low < multiplier <= high:
                buckets[label] += 1
                break
    return buckets


def compute_statistics(batch: SpinBatch, scatter_trigger_threshold: int = 3) -> GameStatistics:
    n = batch.num_spins
    bet = batch.bet
    multipliers = [p / bet for p in batch.payouts]

    mean = sum(multipliers) / n
    variance = sum((x - mean) ** 2 for x in multipliers) / n
    std_dev = math.sqrt(variance)

    if std_dev > 0:
        skewness = (sum((x - mean) ** 3 for x in multipliers) / n) / std_dev**3
        kurtosis = (sum((x - mean) ** 4 for x in multipliers) / n) / std_dev**4 - 3.0
    else:
        skewness = 0.0
        kurtosis = 0.0

    hits = sum(1 for m in multipliers if m > 0)
    hit_frequency = hits / n

    scatter_triggers = sum(1 for c in batch.scatter_counts if c >= scatter_trigger_threshold)
    scatter_trigger_frequency = scatter_triggers / n

    sorted_multipliers = sorted(multipliers)
    percentiles = {p: _percentile(sorted_multipliers, p) for p in (50, 90, 99, 99.9)}

    total_symbols = sum(batch.symbol_counts.values())
    symbol_frequency = (
        {symbol.value: count / total_symbols for symbol, count in batch.symbol_counts.items()}
        if total_symbols
        else {}
    )

    win_histogram = build_win_histogram(batch.payouts, bet)

    return GameStatistics(
        num_spins=n,
        bet=bet,
        rtp=mean,
        house_edge=1.0 - mean,
        mean_payout=mean * bet,
        variance=variance,
        std_dev=std_dev,
        skewness=skewness,
        kurtosis=kurtosis,
        hit_frequency=hit_frequency,
        scatter_trigger_frequency=scatter_trigger_frequency,
        max_win_multiplier=max(multipliers),
        percentiles=percentiles,
        symbol_frequency=symbol_frequency,
        win_histogram=win_histogram,
    )
