import random
from typing import List, Optional

from engine.evaluator import evaluate_spin
from engine.models import Payline, SpinResult
from engine.paytable import Paytable
from engine.reels import ReelSet


class SlotMachine:
    """Ties reels, paylines, and paytable together behind one spin() call.

    This is the only entry point later analysis code (RTP calculator,
    Monte Carlo simulator, volatility analyzer) should ever need.
    """

    def __init__(self, reel_set: ReelSet, paylines: List[Payline], paytable: Paytable):
        self.reel_set = reel_set
        self.paylines = paylines
        self.paytable = paytable

    def spin(self, bet: float = 1.0, rng: Optional[random.Random] = None) -> SpinResult:
        grid = self.reel_set.spin(rng)
        return evaluate_spin(grid, self.paylines, self.paytable, bet)
