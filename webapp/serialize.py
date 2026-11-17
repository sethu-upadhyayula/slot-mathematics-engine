from typing import Any, Dict

from engine.features.free_spins import RoundResult
from engine.models import Grid, SpinResult


def serialize_grid(grid: Grid):
    return [[symbol.value for symbol in column] for column in grid]


def serialize_spin_result(result: SpinResult) -> Dict[str, Any]:
    return {
        "grid": serialize_grid(result.grid),
        "win_lines": [
            {
                "payline_index": win.payline_index,
                "symbol": win.symbol.value,
                "match_count": win.match_count,
                "payout": win.payout,
                "positions": [list(pos) for pos in win.positions],
            }
            for win in result.win_lines
        ],
        "scatter_payout": result.scatter_payout,
        "total_payout": result.total_payout,
    }


def serialize_round_result(result: RoundResult) -> Dict[str, Any]:
    free_spins = None
    if result.free_spins is not None:
        free_spins = {
            "spins_played": result.free_spins.spins_played,
            "retriggers": result.free_spins.retriggers,
            "total_payout": result.free_spins.total_payout,
            "spin_results": [serialize_spin_result(r) for r in result.free_spins.spin_results],
        }

    return {
        "base_spin": serialize_spin_result(result.base_spin),
        "free_spins": free_spins,
        "total_payout": result.total_payout,
    }
