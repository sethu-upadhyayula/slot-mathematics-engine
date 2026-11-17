import math
from dataclasses import dataclass
from typing import List, Protocol

import numpy as np
from scipy import stats

ALPHA = 0.05  # standard significance threshold: reject "looks random" below this p-value


class RandomSource(Protocol):
    def randrange(self, n: int) -> int: ...
    def random(self) -> float: ...


class NumpyGeneratorAdapter:
    """Wraps a numpy.random.Generator so it satisfies the randrange(n)/random()
    interface our engine already expects from random.Random, any NumPy bit
    generator can drive a spin exactly like the standard library RNG does."""

    def __init__(self, bit_generator):
        self._gen = np.random.Generator(bit_generator)

    def randrange(self, n: int) -> int:
        return int(self._gen.integers(0, n))

    def random(self) -> float:
        return float(self._gen.random())


class WeakLCG:
    """A deliberately poor PRNG (small-modulus linear congruential generator)
    used as a negative control. Classic LCG weakness: low-order bits of an
    LCG with a power-of-two modulus have far shorter periods and much worse
    statistical properties than the high-order bits, taking `state % n`
    for small n exposes exactly that flaw. If our tests can't catch this,
    they aren't doing their job."""

    def __init__(self, seed: int = 1):
        self._state = seed % (2**16)
        self._modulus = 2**16
        self._multiplier = 1103515245
        self._increment = 12345

    def _next(self) -> int:
        self._state = (self._multiplier * self._state + self._increment) % self._modulus
        return self._state

    def randrange(self, n: int) -> int:
        return self._next() % n

    def random(self) -> float:
        return self._next() / self._modulus


@dataclass
class ChiSquareResult:
    observed: List[int]
    statistic: float
    p_value: float

    @property
    def passed(self) -> bool:
        return self.p_value >= ALPHA


@dataclass
class KSResult:
    statistic: float
    p_value: float

    @property
    def passed(self) -> bool:
        return self.p_value >= ALPHA


@dataclass
class RunsTestResult:
    num_runs: int
    expected_runs: float
    z_score: float
    p_value: float

    @property
    def passed(self) -> bool:
        return self.p_value >= ALPHA


def chi_square_uniformity_test(source: RandomSource, n_categories: int, num_samples: int) -> ChiSquareResult:
    """Are randrange(n_categories) draws uniformly spread across all categories?"""
    observed = [0] * n_categories
    for _ in range(num_samples):
        observed[source.randrange(n_categories)] += 1

    expected = [num_samples / n_categories] * n_categories
    statistic, p_value = stats.chisquare(observed, expected)
    return ChiSquareResult(observed=observed, statistic=float(statistic), p_value=float(p_value))


def ks_uniformity_test(source: RandomSource, num_samples: int) -> KSResult:
    """Do random() draws match the continuous Uniform(0, 1) distribution?"""
    samples = [source.random() for _ in range(num_samples)]
    statistic, p_value = stats.kstest(samples, "uniform")
    return KSResult(statistic=float(statistic), p_value=float(p_value))


def runs_test(source: RandomSource, num_samples: int) -> RunsTestResult:
    """Wald-Wolfowitz runs test: given a binary sequence, are consecutive
    draws independent, or is there clustering/alternation a real RNG
    shouldn't produce? Too few runs = clustering; too many = alternation."""
    sequence = [source.randrange(2) for _ in range(num_samples)]
    return _runs_test_on_sequence(sequence)


def _runs_test_on_sequence(sequence: List[int]) -> RunsTestResult:
    n1 = sum(sequence)
    n2 = len(sequence) - n1
    n = n1 + n2

    num_runs = 1
    for i in range(1, len(sequence)):
        if sequence[i] != sequence[i - 1]:
            num_runs += 1

    expected_runs = (2 * n1 * n2) / n + 1
    variance = (2 * n1 * n2 * (2 * n1 * n2 - n)) / (n**2 * (n - 1))
    z_score = (num_runs - expected_runs) / math.sqrt(variance)
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

    return RunsTestResult(num_runs=num_runs, expected_runs=expected_runs, z_score=z_score, p_value=p_value)
