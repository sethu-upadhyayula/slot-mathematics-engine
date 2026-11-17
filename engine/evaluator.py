from typing import List, Optional

from engine.models import Grid, Payline, SpinResult, WinLine
from engine.paytable import Paytable
from engine.symbols import Symbol


def evaluate_payline(
    grid: Grid,
    payline: Payline,
    payline_index: int,
    paytable: Paytable,
    bet: float,
) -> Optional[WinLine]:
    """Evaluate a single payline left-to-right. Matches must start on reel 0
    and run contiguously; Wild substitutes for any symbol except Scatter."""

    symbols_on_line = [grid[reel_idx][row] for reel_idx, row in enumerate(payline)]

    if symbols_on_line[0] == Symbol.SCATTER:
        return None

    line_symbol = symbols_on_line[0]
    if line_symbol == Symbol.WILD:
        for symbol in symbols_on_line[1:]:
            if symbol != Symbol.WILD:
                line_symbol = symbol
                break

    match_count = 0
    positions = []
    for reel_idx, symbol in enumerate(symbols_on_line):
        if symbol == line_symbol or symbol == Symbol.WILD:
            match_count += 1
            positions.append((reel_idx, payline[reel_idx]))
        else:
            break

    if match_count < 3:
        return None

    multiplier = paytable.payout_for(line_symbol, match_count)
    if multiplier is None:
        return None

    return WinLine(
        payline_index=payline_index,
        symbol=line_symbol,
        match_count=match_count,
        payout=multiplier * bet,
        positions=positions,
    )


def evaluate_scatter(grid: Grid, paytable: Paytable, bet: float) -> float:
    scatter_count = sum(column.count(Symbol.SCATTER) for column in grid)
    return paytable.scatter_payout_for(scatter_count) * bet


def evaluate_spin(
    grid: Grid,
    paylines: List[Payline],
    paytable: Paytable,
    bet: float,
) -> SpinResult:
    win_lines = []
    for index, payline in enumerate(paylines):
        win = evaluate_payline(grid, payline, index, paytable, bet)
        if win is not None:
            win_lines.append(win)

    scatter_payout = evaluate_scatter(grid, paytable, bet)
    total_payout = sum(win.payout for win in win_lines) + scatter_payout

    return SpinResult(
        grid=grid,
        win_lines=win_lines,
        scatter_payout=scatter_payout,
        total_payout=total_payout,
        bet=bet,
    )
