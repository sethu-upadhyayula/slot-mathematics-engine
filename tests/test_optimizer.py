import random

from analytics.optimizer import (
    build_final_machine,
    build_machine_from_composition,
    optimize_composition,
    perturb_composition,
    random_composition,
    rescale_batch_for_target_rtp,
    scaled_paytable,
)
from analytics.rtp import exact_rtp
from analytics.statistics import compute_statistics
from engine.symbols import Symbol
from simulation.simulate import SpinBatch


def make_batch() -> SpinBatch:
    batch = SpinBatch(bet=1.0)
    batch.payouts = [0, 0, 0, 2, 10]  # raw RTP = 12/5 = 2.4
    batch.scatter_counts = [0, 0, 0, 0, 0]
    return batch


def test_rescale_hits_target_rtp_exactly():
    rescaled, scale = rescale_batch_for_target_rtp(make_batch(), target_rtp=0.96)
    stats = compute_statistics(rescaled)
    assert abs(stats.rtp - 0.96) < 1e-9


def test_rescale_preserves_hit_frequency_and_coefficient_of_variation():
    """The core assumption behind the whole optimizer: uniformly scaling
    every payout changes RTP but leaves hit frequency and CV untouched."""
    raw_stats = compute_statistics(make_batch())
    rescaled, _ = rescale_batch_for_target_rtp(make_batch(), target_rtp=0.5)

    rescaled_stats = compute_statistics(rescaled)

    assert rescaled_stats.hit_frequency == raw_stats.hit_frequency
    assert abs(rescaled_stats.coefficient_of_variation - raw_stats.coefficient_of_variation) < 1e-9
    assert abs(rescaled_stats.skewness - raw_stats.skewness) < 1e-9


def test_perturb_composition_keeps_total_fixed_and_respects_floor():
    composition = {Symbol.CHERRY: 5, Symbol.LEMON: 1, Symbol.ORANGE: 14}
    rng = random.Random(0)

    for _ in range(50):
        composition = perturb_composition(composition, rng, min_count=1)
        assert sum(composition.values()) == 20
        assert all(count >= 1 for count in composition.values())


def test_random_composition_respects_total_and_floor():
    template = {Symbol.CHERRY: 5, Symbol.LEMON: 4, Symbol.WILD: 1}
    rng = random.Random(1)

    composition = random_composition(template, rng, min_count=1)

    assert sum(composition.values()) == sum(template.values())
    assert all(count >= 1 for count in composition.values())


def test_paytable_scaling_scales_exact_rtp_linearly():
    """Directly verifies the linear-scaling assumption the optimizer relies
    on to correct RTP without re-simulating: doubling every payout doubles
    exact RTP exactly, for a fixed reel/payline structure."""
    composition = {Symbol.CHERRY: 10, Symbol.LEMON: 10}
    template_paytable = {(Symbol.CHERRY, 3): 4.0}
    paylines = [[0, 0, 0]]

    machine_1x = build_machine_from_composition(composition, template_paytable, {}, paylines, num_reels=3, num_rows=1)
    machine_2x = build_machine_from_composition(composition, template_paytable, {}, paylines, num_reels=3, num_rows=1)
    machine_2x.paytable = scaled_paytable(machine_2x.paytable, 2.0)

    assert abs(exact_rtp(machine_2x) - 2 * exact_rtp(machine_1x)) < 1e-9


def test_optimize_composition_runs_and_preserves_invariants():
    paylines = [[1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [2, 2, 2, 2, 2]]
    template_paytable = {
        (Symbol.CHERRY, 3): 2, (Symbol.CHERRY, 4): 4, (Symbol.CHERRY, 5): 8,
        (Symbol.WILD, 3): 10, (Symbol.WILD, 4): 20, (Symbol.WILD, 5): 50,
    }
    template_scatter_paytable = {3: 1, 4: 5, 5: 20}
    seed_composition = {
        Symbol.CHERRY: 8, Symbol.LEMON: 6, Symbol.WILD: 3, Symbol.SCATTER: 3,
    }

    result = optimize_composition(
        seed_composition=seed_composition,
        template_paytable=template_paytable,
        template_scatter_paytable=template_scatter_paytable,
        paylines=paylines,
        target_rtp=0.96,
        target_hit_frequency=0.25,
        target_cv=2.0,
        num_reels=5,
        num_rows=3,
        search_spins=2_000,
        iterations_per_restart=5,
        restarts=2,
        rng=random.Random(7),
    )

    assert len(result.history) == 2 * (5 + 1)
    assert sum(result.best_composition.values()) == sum(seed_composition.values())
    # The rescale step forces this to be exact (up to floating point), regardless of MC noise.
    assert abs(result.best_stats.rtp - 0.96) < 1e-9

    # The scale itself was estimated from a noisy 2,000-spin sample, so the true
    # (exactly enumerated) RTP of the final machine is only approximately on target.
    final_machine = build_final_machine(
        result, template_paytable, template_scatter_paytable, paylines, num_reels=5, num_rows=3
    )
    assert abs(exact_rtp(final_machine) - 0.96) < 0.15
