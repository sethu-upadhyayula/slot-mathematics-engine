import json
import random
import time
from pathlib import Path

from analytics.optimizer import build_machine_from_composition, optimize_composition, scaled_paytable
from analytics.report import print_statistics_report
from analytics.rtp import exact_rtp
from analytics.statistics import compute_statistics
from engine.config import load_template_paytable, machine_to_game_config
from engine.symbols import Symbol
from simulation.simulate import run_spins

REPO_ROOT = Path(__file__).resolve().parent.parent

TARGET_RTP = 0.96
TARGET_HIT_FREQUENCY = 0.30
TARGET_CV = 2.5  # "medium" volatility: Phase 4's low-vol machine measured ~1.9, high-vol ~3.7


def main() -> None:
    paylines, template_paytable, template_scatter_paytable = load_template_paytable(
        str(REPO_ROOT / "configs" / "default_game.json")
    )

    seed_composition = {
        Symbol.CHERRY: 5,
        Symbol.LEMON: 4,
        Symbol.ORANGE: 3,
        Symbol.PLUM: 3,
        Symbol.BAR: 2,
        Symbol.SEVEN: 1,
        Symbol.WILD: 1,
        Symbol.SCATTER: 1,
    }

    print(f"Target: RTP={TARGET_RTP:.0%}, hit frequency={TARGET_HIT_FREQUENCY:.0%}, CV={TARGET_CV}")
    print("Searching reel compositions (RTP corrected for free at every step)...")

    start = time.perf_counter()
    result = optimize_composition(
        seed_composition=seed_composition,
        template_paytable=template_paytable,
        template_scatter_paytable=template_scatter_paytable,
        paylines=paylines,
        target_rtp=TARGET_RTP,
        target_hit_frequency=TARGET_HIT_FREQUENCY,
        target_cv=TARGET_CV,
        num_reels=5,
        num_rows=3,
        search_spins=30_000,
        iterations_per_restart=50,
        restarts=3,
        rng=random.Random(42),
    )
    elapsed = time.perf_counter() - start

    print(f"\nSearch complete in {elapsed:.1f}s ({len(result.history)} compositions evaluated)")
    print(f"Best fitness: {result.best_fitness:.6f}")
    print("Best composition (per reel, all 5 reels identical):")
    for symbol, count in result.best_composition.items():
        print(f"  {symbol.value:<8}: {count}")
    print(f"Paytable scale applied: {result.best_scale:.4f}")
    print()
    print_statistics_report(result.best_stats, title="Search-time estimate (30K spins)")

    # The search's paytable scale came from a noisy 30K-spin sample, fine for
    # steering hit frequency/CV, but not precise enough for the final RTP. Reel
    # strips are still short enough (20 stops) for exact enumeration, so
    # recalibrate the scale exactly for the chosen composition as a final step.
    unscaled_machine = build_machine_from_composition(
        result.best_composition, template_paytable, template_scatter_paytable, paylines, num_reels=5, num_rows=3
    )
    raw_exact_rtp = exact_rtp(unscaled_machine)
    precise_scale = TARGET_RTP / raw_exact_rtp
    final_machine = build_machine_from_composition(
        result.best_composition, template_paytable, template_scatter_paytable, paylines, num_reels=5, num_rows=3
    )
    final_machine.paytable = scaled_paytable(final_machine.paytable, precise_scale)

    print(f"\nSearch-time scale was {result.best_scale:.4f} (from a 30K-spin sample)")
    print(f"Recalibrated scale is {precise_scale:.4f} (from exact enumeration)")

    print("\nConfirming with exact enumeration and a larger Monte Carlo sample...")
    exact = exact_rtp(final_machine)
    confirm_batch = run_spins(final_machine, 2_000_000, bet=1.0, rng=random.Random(123))
    confirm_stats = compute_statistics(confirm_batch)
    print(f"Exact RTP: {exact:.4%}")
    print()
    print_statistics_report(confirm_stats, title="Confirmation (2M spins)")

    config_path = REPO_ROOT / "configs" / "optimized_game.json"
    config = machine_to_game_config(
        final_machine,
        description=(
            f"Auto-tuned by scripts/run_optimizer.py to hit RTP={TARGET_RTP:.0%}, "
            f"hit_frequency={TARGET_HIT_FREQUENCY:.0%}, CV={TARGET_CV}."
        ),
    )
    config_path.write_text(json.dumps(config, indent=2))
    print(f"\nWrote tuned config to {config_path}")


if __name__ == "__main__":
    main()
