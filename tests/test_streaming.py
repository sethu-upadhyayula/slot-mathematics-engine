import random
import statistics
import tracemalloc

from engine.config import load_game_config
from simulation.simulate import run_spins
from simulation.streaming import StreamingStats, run_spins_streaming


def test_streaming_mean_and_variance_match_naive_computation():
    values = [0.0, 0.0, 5.0, 10.0, 2.5, 0.0, 100.0, 0.0]

    accumulator = StreamingStats(bet=1.0)
    for value in values:
        accumulator.update(payout=value, scatter_count=0)

    assert accumulator.num_spins == len(values)
    assert abs(accumulator.mean - statistics.mean(values)) < 1e-9
    assert abs(accumulator.variance - statistics.pvariance(values)) < 1e-9


def test_streaming_hit_frequency_and_max_payout():
    accumulator = StreamingStats(bet=1.0)
    for value in [0.0, 0.0, 3.0, 0.0, 7.5]:
        accumulator.update(payout=value, scatter_count=0)

    assert accumulator.hits == 2
    assert accumulator.hit_frequency == 2 / 5
    assert accumulator.max_payout == 7.5


def test_streaming_scatter_trigger_threshold():
    accumulator = StreamingStats(bet=1.0)
    for scatter_count in [0, 2, 3, 4, 3]:
        accumulator.update(payout=0.0, scatter_count=scatter_count, scatter_trigger_threshold=3)

    assert accumulator.scatter_triggers == 3
    assert accumulator.scatter_trigger_frequency == 3 / 5


def test_confidence_interval_narrows_with_more_spins():
    rng = random.Random(0)
    machine = load_game_config("configs/default_game.json")

    small = run_spins_streaming(machine, 5_000, bet=1.0, rng=rng, track_symbol_counts=False)
    large = run_spins_streaming(machine, 50_000, bet=1.0, rng=rng, track_symbol_counts=False)

    small_width = small.confidence_interval_95[1] - small.confidence_interval_95[0]
    large_width = large.confidence_interval_95[1] - large.confidence_interval_95[0]

    assert large_width < small_width


def test_streaming_rtp_matches_batch_rtp_on_same_seed():
    machine = load_game_config("configs/default_game.json")

    batch = run_spins(machine, 20_000, bet=1.0, rng=random.Random(99))
    streaming = run_spins_streaming(machine, 20_000, bet=1.0, rng=random.Random(99))

    batch_rtp = sum(batch.payouts) / (batch.num_spins * batch.bet)
    assert abs(streaming.rtp - batch_rtp) < 1e-9


def test_streaming_uses_far_less_memory_than_batch_at_scale():
    machine = load_game_config("configs/default_game.json")
    num_spins = 100_000

    tracemalloc.start()
    run_spins(machine, num_spins, bet=1.0, rng=random.Random(1))
    _, batch_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    tracemalloc.start()
    run_spins_streaming(machine, num_spins, bet=1.0, rng=random.Random(1))
    _, streaming_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert streaming_peak < batch_peak / 5
