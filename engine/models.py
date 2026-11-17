from dataclasses import dataclass
from typing import List, Tuple

from engine.symbols import Symbol

Grid = List[List[Symbol]]  # grid[reel_index][row_index]
Payline = List[int]  # row index to read on each reel


@dataclass
class WinLine:
    payline_index: int
    symbol: Symbol
    match_count: int
    payout: float
    positions: List[Tuple[int, int]]  # (reel_index, row_index)


@dataclass
class SpinResult:
    grid: Grid
    win_lines: List[WinLine]
    scatter_payout: float
    total_payout: float
    bet: float

    @property
    def win_multiplier(self) -> float:
        return self.total_payout / self.bet if self.bet else 0.0
