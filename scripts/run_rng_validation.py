import random
from pathlib import Path

import numpy as np

from analytics.rng_fairness import (
    NumpyGeneratorAdapter,
    WeakLCG,
    chi_square_uniformity_test,
    ks_uniformity_test,
    runs_test,
)
from analytics.rtp import exact_rtp
from engine.config import load_game_config
from simulation.simulate import run_spins

REPO_ROOT = Path(__file__).resolve().parent.parent
SEED = 12345

RNG_SOURCES = {
    "Python random (MT19937)": random.Random(SEED),
    "NumPy MT19937": NumpyGeneratorAdapter(np.random.MT19937(SEED)),
    "NumPy PCG64 (NumPy's default)": NumpyGeneratorAdapter(np.random.PCG64(SEED)),
    "NumPy SFC64": NumpyGeneratorAdapter(np.random.SFC64(SEED)),
    "Weak LCG (negative control)": WeakLCG(SEED),
}


def print_fairness_table() -> None:
    print("=== Statistical fairness tests (alpha=0.05) ===\n")
    header = f"{'RNG':<32} {'Chi2 p':>10} {'':>6} {'KS p':>10} {'':>6} {'Runs p':>10} {'':>6}"
    print(header)
    print("-" * len(header))

    for name, source in RNG_SOURCES.items():
        chi2 = chi_square_uniformity_test(source, n_categories=20, num_samples=200_000)
        ks = ks_uniformity_test(source, num_samples=100_000)
        runs = runs_test(source, num_samples=100_000)

        def mark(passed: bool) -> str:
            return "PASS" if passed else "FAIL"

        print(
            f"{name:<32} {chi2.p_value:>10.4f} {mark(chi2.passed):>6} "
            f"{ks.p_value:>10.4f} {mark(ks.passed):>6} "
            f"{runs.p_value:>10.4f} {mark(runs.passed):>6}"
        )


def print_engine_consequence_table() -> None:
    print("\n=== Same RNGs, plugged into the actual slot engine ===\n")
    machine = load_game_config(str(REPO_ROOT / "configs" / "default_game.json"))
    known_exact_rtp = exact_rtp(machine)
    print(f"Known exact RTP (Phase 2): {known_exact_rtp:.4%}\n")

    header = f"{'RNG':<32} {'Measured RTP':>14} {'Diff from exact':>18}"
    print(header)
    print("-" * len(header))

    num_spins = 300_000
    for name, source in RNG_SOURCES.items():
        batch = run_spins(machine, num_spins, bet=1.0, rng=source)
        measured_rtp = sum(batch.payouts) / (num_spins * batch.bet)
        diff = measured_rtp - known_exact_rtp
        print(f"{name:<32} {measured_rtp:>14.4%} {diff:>+18.4%}")


def main() -> None:
    print_fairness_table()
    print_engine_consequence_table()
    print(
        "\nNote: the engine only ever calls .randrange(n) on whatever RNG object "
        "it's given, it never imports random or numpy directly. Any of these "
        "sources plug in as a drop-in replacement, which is exactly what the "
        "NumpyGeneratorAdapter demonstrates."
    )


if __name__ == "__main__":
    main()
