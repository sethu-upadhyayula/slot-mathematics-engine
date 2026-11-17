import time

from analytics.report import print_statistics_report
from analytics.rtp import exact_rtp
from analytics.statistics import compute_statistics
from engine.config import load_game_config
from simulation.simulate import run_spins

NUM_SPINS = 2_000_000


def run_one(path: str, title: str) -> None:
    machine = load_game_config(path)

    start = time.perf_counter()
    batch = run_spins(machine, NUM_SPINS)
    elapsed = time.perf_counter() - start

    stats = compute_statistics(batch)
    print_statistics_report(stats, title=title)
    print(f"(exact RTP: {exact_rtp(machine):.4%}, simulated {NUM_SPINS:,} spins in {elapsed:.1f}s)")
    print()


def main() -> None:
    run_one("configs/volatility_low.json", "Machine A - Low Volatility")
    run_one("configs/volatility_high.json", "Machine B - High Volatility")


if __name__ == "__main__":
    main()
