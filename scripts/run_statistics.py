import time

from analytics.report import print_statistics_report
from analytics.statistics import compute_statistics
from engine.config import load_game_config
from simulation.simulate import run_spins


def main() -> None:
    machine = load_game_config("configs/default_game.json")
    num_spins = 2_000_000

    start = time.perf_counter()
    batch = run_spins(machine, num_spins)
    elapsed = time.perf_counter() - start

    stats = compute_statistics(batch)
    print_statistics_report(stats, title="Default Game")
    print(f"(simulated {num_spins:,} spins in {elapsed:.1f}s)")


if __name__ == "__main__":
    main()
