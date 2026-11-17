import random

from analytics.rtp import exact_rtp, monte_carlo_rtp, total_combinations
from engine.paytable import Paytable
from engine.reels import ReelSet, ReelStrip
from engine.slot_machine import SlotMachine
from engine.symbols import Symbol


def make_tiny_machine() -> SlotMachine:
    """3 reels x 2 stops each, one payline, only 3xCHERRY pays.

    Small enough to hand-verify: 8 equally likely combinations, exactly
    1 of them (CHERRY, CHERRY, CHERRY) wins, paying 10x bet.
    Expected RTP = 10/8 = 125%.
    """
    reels = [ReelStrip([Symbol.CHERRY, Symbol.LEMON]) for _ in range(3)]
    reel_set = ReelSet(reels, num_rows=1)
    paytable = Paytable(payouts={(Symbol.CHERRY, 3): 10}, scatter_payouts={})
    paylines = [[0, 0, 0]]
    return SlotMachine(reel_set, paylines, paytable)


def test_total_combinations_is_product_of_reel_lengths():
    machine = make_tiny_machine()
    assert total_combinations(machine) == 8


def test_exact_rtp_matches_hand_calculation():
    machine = make_tiny_machine()
    assert exact_rtp(machine) == 10 / 8


def test_monte_carlo_rtp_converges_toward_exact_value():
    machine = make_tiny_machine()
    rng = random.Random(42)

    estimate = monte_carlo_rtp(machine, num_spins=200_000, rng=rng)

    assert abs(estimate - exact_rtp(machine)) < 0.02
