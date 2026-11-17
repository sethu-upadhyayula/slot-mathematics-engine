import random
import time

from engine.config import load_game_config
from engine.features.free_spins import FreeSpinsConfig, play_round

NUM_SPINS = 500_000


def main() -> None:
    machine = load_game_config("configs/full_game_with_bonus.json")
    config = FreeSpinsConfig(
        trigger_scatter_count=3,
        spins_awarded=10,
        retrigger_scatter_count=3,
        retrigger_spins_awarded=5,
        sticky_wilds=True,
    )
    rng = random.Random(0)

    base_payout_total = 0.0
    bonus_payout_total = 0.0
    bonus_triggers = 0

    start = time.perf_counter()
    for _ in range(NUM_SPINS):
        result = play_round(machine, config, bet=1.0, rng=rng)
        base_payout_total += result.base_spin.total_payout
        if result.free_spins is not None:
            bonus_payout_total += result.free_spins.total_payout
            bonus_triggers += 1
    elapsed = time.perf_counter() - start

    total_payout = base_payout_total + bonus_payout_total
    total_rtp = total_payout / NUM_SPINS
    base_rtp_contribution = base_payout_total / NUM_SPINS
    bonus_rtp_contribution = bonus_payout_total / NUM_SPINS

    print(f"Simulated {NUM_SPINS:,} base spins (each may trigger a free spins round) in {elapsed:.1f}s")
    print(f"Bonus trigger frequency: {bonus_triggers / NUM_SPINS:.4%}")
    print()
    print(f"Total RTP:               {total_rtp:.4%}")
    print(f"  from base game:        {base_rtp_contribution:.4%} ({base_rtp_contribution / total_rtp:.1%} of total)")
    print(f"  from free spins bonus: {bonus_rtp_contribution:.4%} ({bonus_rtp_contribution / total_rtp:.1%} of total)")


if __name__ == "__main__":
    main()
