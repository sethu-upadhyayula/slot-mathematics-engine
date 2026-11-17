import time

from analytics.rtp import exact_rtp, monte_carlo_rtp, total_combinations
from engine.config import load_game_config


def main() -> None:
    machine = load_game_config("configs/default_game.json")

    combos = total_combinations(machine)
    print(f"Total reel-stop combinations: {combos:,}")

    start = time.perf_counter()
    exact = exact_rtp(machine)
    elapsed = time.perf_counter() - start
    print(f"Exact RTP:       {exact:.4%}   (enumerated in {elapsed:.1f}s)")
    print()

    for num_spins in (10_000, 100_000, 1_000_000):
        start = time.perf_counter()
        estimate = monte_carlo_rtp(machine, num_spins)
        elapsed = time.perf_counter() - start
        diff = estimate - exact
        print(
            f"Monte Carlo RTP ({num_spins:>9,} spins): {estimate:.4%}   "
            f"(diff from exact: {diff:+.4%}, {elapsed:.1f}s)"
        )


if __name__ == "__main__":
    main()
