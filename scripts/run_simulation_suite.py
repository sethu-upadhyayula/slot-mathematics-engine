import random
import time
import tracemalloc
from pathlib import Path

from engine.config import load_game_config
from simulation.simulate import run_spins
from simulation.streaming import run_spins_streaming

REPO_ROOT = Path(__file__).resolve().parent.parent

# Measured separately (see docs/phase8_simulation_suite.md): at ~95K spins/sec,
# a 100M-spin run in this pure-Python engine takes ~17-18 minutes, longer
# than this tool's own hard execution ceiling allows in one call. That's the
# real finding, not a rounding choice: pure Python doesn't scale to
# certification-grade spin counts without a compiled/vectorized engine.
MEMORY_BENCHMARK_SPINS = [100_000, 500_000]
SUITE_SPIN_COUNTS = [1_000_000, 10_000_000]


def benchmark_memory(machine, num_spins: int):
    tracemalloc.start()
    run_spins(machine, num_spins, bet=1.0, rng=random.Random(1))
    _, batch_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    tracemalloc.start()
    run_spins_streaming(machine, num_spins, bet=1.0, rng=random.Random(1))
    _, streaming_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return batch_peak, streaming_peak


def main() -> None:
    machine = load_game_config(str(REPO_ROOT / "configs" / "default_game.json"))

    print("=== Memory: batch (stores every spin) vs. streaming (Welford, O(1)) ===\n")
    header = f"{'Spins':>12} {'Batch peak (MB)':>18} {'Streaming peak (MB)':>22} {'Ratio':>10}"
    print(header)
    print("-" * len(header))
    for num_spins in MEMORY_BENCHMARK_SPINS:
        batch_peak, streaming_peak = benchmark_memory(machine, num_spins)
        ratio = batch_peak / streaming_peak
        print(f"{num_spins:>12,} {batch_peak / 1e6:>18.1f} {streaming_peak / 1e6:>22.2f} {ratio:>9.0f}x")

    print("\n=== Simulation suite: runtime, throughput, confidence interval ===\n")
    header = f"{'Spins':>12} {'Runtime (s)':>12} {'Spins/sec':>14} {'RTP estimate':>14} {'95% CI':>24}"
    print(header)
    print("-" * len(header))

    measured_throughput = None
    for num_spins in SUITE_SPIN_COUNTS:
        start = time.perf_counter()
        stats = run_spins_streaming(machine, num_spins, bet=1.0, rng=random.Random(42), track_symbol_counts=False)
        elapsed = time.perf_counter() - start
        throughput = num_spins / elapsed
        measured_throughput = throughput
        ci_low, ci_high = stats.confidence_interval_95
        ci_text = f"[{ci_low:.4%}, {ci_high:.4%}]"
        print(f"{num_spins:>12,} {elapsed:>12.1f} {throughput:>14,.0f} {stats.rtp:>14.4%} {ci_text:>24}")

    hundred_million = 100_000_000
    estimated_seconds = hundred_million / measured_throughput
    print(
        f"\n100,000,000 spins: NOT run (would take an estimated "
        f"{estimated_seconds / 60:.1f} minutes at this measured throughput: "
        f"exceeds what's practical for pure Python in a single run)."
    )
    print(
        "This is the real conclusion of this phase: a bounded-memory streaming "
        "accumulator solves the *memory* half of scaling to certification-grade "
        "spin counts, but pure Python throughput is still the bottleneck. Reaching "
        "100M+ spins in reasonable wall-clock time needs a compiled or vectorized "
        "engine (NumPy batch simulation, or a Rust/C extension), not just better "
        "bookkeeping."
    )


if __name__ == "__main__":
    main()
