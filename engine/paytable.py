from typing import Dict, Optional, Tuple

from engine.symbols import Symbol


class Paytable:
    """Payout multipliers (relative to bet) for line wins and scatter wins."""

    def __init__(
        self,
        payouts: Dict[Tuple[Symbol, int], float],
        scatter_payouts: Dict[int, float],
    ):
        self.payouts = payouts
        self.scatter_payouts = scatter_payouts

    def payout_for(self, symbol: Symbol, match_count: int) -> Optional[float]:
        return self.payouts.get((symbol, match_count))

    def scatter_payout_for(self, count: int) -> float:
        return self.scatter_payouts.get(count, 0.0)
