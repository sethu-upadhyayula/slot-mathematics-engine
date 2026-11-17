import random
from typing import List, Optional

from engine.symbols import Symbol


class ReelStrip:
    """A single reel: a fixed sequence of symbols wrapped in a loop.

    The stop position determines which symbol lines up with the top
    of the visible window; the window then reads downward, wrapping
    around the end of the strip.
    """

    def __init__(self, symbols: List[Symbol]):
        self.symbols = symbols
        self.length = len(symbols)

    def spin(self, rng: Optional[random.Random] = None) -> int:
        rng = rng or random
        return rng.randrange(self.length)

    def window(self, stop: int, num_rows: int) -> List[Symbol]:
        return [self.symbols[(stop + i) % self.length] for i in range(num_rows)]


class ReelSet:
    """The full set of reels that make up a spin."""

    def __init__(self, reels: List[ReelStrip], num_rows: int = 3):
        self.reels = reels
        self.num_rows = num_rows
        self.num_reels = len(reels)

    def spin(self, rng: Optional[random.Random] = None) -> List[List[Symbol]]:
        stops = [reel.spin(rng) for reel in self.reels]
        return self.grid_from_stops(stops)

    def grid_from_stops(self, stops: List[int]) -> List[List[Symbol]]:
        return [reel.window(stop, self.num_rows) for reel, stop in zip(self.reels, stops)]
