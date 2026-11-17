from analytics.statistics import compute_statistics
from simulation.simulate import SpinBatch


def make_batch() -> SpinBatch:
    """5 spins, bet=1: four losses and one 10x win, plus a scatter trigger
    on the winning spin. Hand-computed expectations below.

    multipliers = [0, 0, 0, 0, 10]
    mean = 2.0
    variance = ((4 * (0-2)**2) + (10-2)**2) / 5 = (16 + 64) / 5 = 16.0
    std_dev = 4.0
    """
    batch = SpinBatch(bet=1.0)
    batch.payouts = [0, 0, 0, 0, 10]
    batch.scatter_counts = [0, 0, 0, 0, 3]
    return batch


def test_rtp_and_house_edge():
    stats = compute_statistics(make_batch())
    assert stats.rtp == 2.0
    assert stats.house_edge == 1.0 - 2.0


def test_variance_and_std_dev():
    stats = compute_statistics(make_batch())
    assert stats.variance == 16.0
    assert stats.std_dev == 4.0


def test_hit_frequency_counts_nonzero_payouts_only():
    stats = compute_statistics(make_batch())
    assert stats.hit_frequency == 1 / 5


def test_scatter_trigger_frequency_respects_threshold():
    stats = compute_statistics(make_batch(), scatter_trigger_threshold=3)
    assert stats.scatter_trigger_frequency == 1 / 5


def test_max_and_median_multiplier():
    stats = compute_statistics(make_batch())
    assert stats.max_win_multiplier == 10
    assert stats.median_win_multiplier == 0  # 3 of 5 values are 0, median falls there


def test_win_histogram_buckets_the_single_win_correctly():
    stats = compute_statistics(make_batch())
    assert stats.win_histogram["0x (no win)"] == 4
    assert stats.win_histogram["(5x, 20x]"] == 1
    assert sum(stats.win_histogram.values()) == 5
