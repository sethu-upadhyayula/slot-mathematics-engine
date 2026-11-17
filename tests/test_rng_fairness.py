import random

import numpy as np

from analytics.rng_fairness import (
    NumpyGeneratorAdapter,
    WeakLCG,
    _runs_test_on_sequence,
    chi_square_uniformity_test,
    ks_uniformity_test,
    runs_test,
)


class _CyclicSource:
    """Deterministic fake source cycling through a fixed sequence, for
    testing the statistical tests themselves against known-shape input,
    independent of any real RNG's behavior."""

    def __init__(self, sequence):
        self._sequence = sequence
        self._index = 0

    def randrange(self, n):
        value = self._sequence[self._index % len(self._sequence)]
        self._index += 1
        return value


def test_chi_square_passes_a_perfectly_uniform_sequence():
    source = _CyclicSource(list(range(20)))
    result = chi_square_uniformity_test(source, n_categories=20, num_samples=2000)

    assert result.observed == [100] * 20
    assert result.statistic == 0.0
    assert result.p_value == 1.0
    assert result.passed


def test_chi_square_catches_an_obviously_biased_source():
    source = _CyclicSource([0])  # always returns 0
    result = chi_square_uniformity_test(source, n_categories=20, num_samples=2000)

    assert not result.passed
    assert result.p_value < 0.001


def test_runs_test_on_alternating_sequence_has_too_many_runs():
    sequence = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    result = _runs_test_on_sequence(sequence)

    assert result.num_runs == 10
    assert result.expected_runs == 6.0
    assert result.z_score > 0  # more runs than expected
    assert not result.passed  # perfect alternation isn't random either


def test_runs_test_on_clustered_sequence_has_too_few_runs():
    sequence = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    result = _runs_test_on_sequence(sequence)

    assert result.num_runs == 2
    assert result.expected_runs == 6.0
    assert result.z_score < 0  # fewer runs than expected (clustering)
    assert not result.passed


def test_a_real_rng_generally_passes_all_three_tests():
    source = random.Random(42)

    chi2 = chi_square_uniformity_test(source, n_categories=20, num_samples=50_000)
    ks = ks_uniformity_test(source, num_samples=50_000)
    runs = runs_test(source, num_samples=50_000)

    assert chi2.passed
    assert ks.passed
    assert runs.passed


def test_numpy_adapter_produces_values_in_range():
    adapter = NumpyGeneratorAdapter(np.random.PCG64(seed=1))

    for _ in range(1000):
        value = adapter.randrange(20)
        assert 0 <= value < 20

    for _ in range(1000):
        value = adapter.random()
        assert 0.0 <= value < 1.0


def test_numpy_adapter_passes_the_fairness_tests():
    adapter = NumpyGeneratorAdapter(np.random.PCG64(seed=1))

    chi2 = chi_square_uniformity_test(adapter, n_categories=20, num_samples=50_000)
    ks = ks_uniformity_test(adapter, num_samples=50_000)

    assert chi2.passed
    assert ks.passed


def test_weak_lcg_is_deterministic_given_a_seed():
    a = WeakLCG(seed=7)
    b = WeakLCG(seed=7)

    sequence_a = [a.randrange(20) for _ in range(100)]
    sequence_b = [b.randrange(20) for _ in range(100)]

    assert sequence_a == sequence_b


def test_weak_lcg_fails_at_least_one_fairness_test():
    """The whole point of including a known-bad RNG: prove the test suite
    actually has the power to catch it, not just wave every RNG through."""
    source = WeakLCG(seed=1)

    chi2 = chi_square_uniformity_test(source, n_categories=20, num_samples=50_000)
    ks = ks_uniformity_test(source, num_samples=50_000)
    runs = runs_test(source, num_samples=50_000)

    assert not (chi2.passed and ks.passed and runs.passed)
