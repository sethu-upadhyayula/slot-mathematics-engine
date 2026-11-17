from engine.evaluator import evaluate_payline, evaluate_scatter
from engine.paytable import Paytable
from engine.symbols import Symbol


def make_paytable() -> Paytable:
    payouts = {
        (Symbol.CHERRY, 3): 5,
        (Symbol.CHERRY, 4): 10,
        (Symbol.CHERRY, 5): 20,
        (Symbol.WILD, 5): 500,
    }
    scatter_payouts = {3: 2, 4: 10, 5: 50}
    return Paytable(payouts, scatter_payouts)


def test_three_of_a_kind_wins_on_payline():
    grid = [
        [Symbol.CHERRY, Symbol.LEMON, Symbol.PLUM],
        [Symbol.CHERRY, Symbol.LEMON, Symbol.PLUM],
        [Symbol.CHERRY, Symbol.LEMON, Symbol.PLUM],
        [Symbol.ORANGE, Symbol.LEMON, Symbol.PLUM],
        [Symbol.BAR, Symbol.LEMON, Symbol.PLUM],
    ]
    payline = [0, 0, 0, 0, 0]

    win = evaluate_payline(grid, payline, 0, make_paytable(), bet=1.0)

    assert win is not None
    assert win.symbol == Symbol.CHERRY
    assert win.match_count == 3
    assert win.payout == 5.0


def test_wild_extends_the_match():
    grid = [
        [Symbol.CHERRY],
        [Symbol.WILD],
        [Symbol.CHERRY],
        [Symbol.CHERRY],
        [Symbol.LEMON],
    ]
    payline = [0, 0, 0, 0, 0]

    win = evaluate_payline(grid, payline, 0, make_paytable(), bet=1.0)

    assert win is not None
    assert win.symbol == Symbol.CHERRY
    assert win.match_count == 4


def test_match_must_start_on_leftmost_reel():
    grid = [
        [Symbol.LEMON],
        [Symbol.CHERRY],
        [Symbol.CHERRY],
        [Symbol.CHERRY],
        [Symbol.CHERRY],
    ]
    payline = [0, 0, 0, 0, 0]

    win = evaluate_payline(grid, payline, 0, make_paytable(), bet=1.0)

    assert win is None


def test_scatter_pays_on_count_regardless_of_position():
    grid = [
        [Symbol.SCATTER, Symbol.LEMON, Symbol.PLUM],
        [Symbol.CHERRY, Symbol.SCATTER, Symbol.PLUM],
        [Symbol.CHERRY, Symbol.LEMON, Symbol.SCATTER],
        [Symbol.ORANGE, Symbol.LEMON, Symbol.PLUM],
        [Symbol.BAR, Symbol.LEMON, Symbol.PLUM],
    ]

    payout = evaluate_scatter(grid, make_paytable(), bet=1.0)

    assert payout == 2.0


def test_scatter_symbols_do_not_pay_on_a_payline():
    grid = [
        [Symbol.SCATTER],
        [Symbol.SCATTER],
        [Symbol.SCATTER],
        [Symbol.SCATTER],
        [Symbol.SCATTER],
    ]
    payline = [0, 0, 0, 0, 0]

    win = evaluate_payline(grid, payline, 0, make_paytable(), bet=1.0)

    assert win is None
