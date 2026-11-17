import random

from engine.config import load_game_config
from engine.display import format_grid
from engine.features.cascade import run_cascade
from engine.features.expanding_wild import spin_with_expanding_wilds
from engine.features.free_spins import FreeSpinsConfig, play_round


def demo_expanding_wild(machine, rng: random.Random) -> None:
    print("=== Expanding Wild ===")
    for _ in range(200):
        result = spin_with_expanding_wilds(machine, bet=1.0, rng=rng)
        if any("WILD" == s.value for column in result.grid for s in column) and result.total_payout > 0:
            print(format_grid(result.grid))
            print(f"Total payout: {result.total_payout}")
            for win in result.win_lines:
                print(f"  Payline {win.payline_index}: {win.match_count}x {win.symbol.value} -> {win.payout}")
            return
    print("(no wild-driven win found in 200 tries with this seed)")


def demo_cascade(machine, rng: random.Random) -> None:
    print("\n=== Cascade ===")
    for _ in range(500):
        result = run_cascade(machine, bet=1.0, rng=rng, multiplier_progression=[1, 2, 3, 5])
        if result.num_cascades >= 2:
            print(f"Initial grid:\n{format_grid(result.initial_grid)}")
            for i, step in enumerate(result.steps):
                print(
                    f"  Cascade {i + 1}: base payout {step.base_payout:.2f} "
                    f"x{step.multiplier} = {step.payout:.2f}"
                )
            print(f"Total payout (incl. scatter): {result.total_payout:.2f}")
            return
    print("(no multi-cascade win found in 500 tries with this seed)")


def demo_free_spins(machine, rng: random.Random) -> None:
    print("\n=== Free Spins with Sticky Wilds and Retriggers ===")
    config = FreeSpinsConfig(
        trigger_scatter_count=3,
        spins_awarded=10,
        retrigger_scatter_count=3,
        retrigger_spins_awarded=5,
        sticky_wilds=True,
    )

    for _ in range(2000):
        result = play_round(machine, config, bet=1.0, rng=rng)
        if result.free_spins is not None:
            print("Base spin triggered the bonus:")
            print(format_grid(result.base_spin.grid))
            fs = result.free_spins
            print(f"\nFree spins played: {fs.spins_played} (retriggers: {fs.retriggers})")
            print(f"Free spins payout: {fs.total_payout:.2f}")
            print(f"Total round payout: {result.total_payout:.2f}")
            return
    print("(no bonus trigger found in 2000 tries with this seed)")


def main() -> None:
    machine = load_game_config("configs/full_game_with_bonus.json")
    rng = random.Random(7)

    demo_expanding_wild(machine, rng)
    demo_cascade(machine, rng)
    demo_free_spins(machine, rng)


if __name__ == "__main__":
    main()
