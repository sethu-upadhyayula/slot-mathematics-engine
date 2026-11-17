import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from analytics.statistics import GameStatistics, compute_statistics
from engine.models import Payline
from engine.paytable import Paytable
from engine.reels import ReelSet, ReelStrip
from engine.slot_machine import SlotMachine
from engine.symbols import Symbol
from simulation.simulate import SpinBatch, run_spins

Composition = Dict[Symbol, int]
TemplatePaytable = Dict[Tuple[Symbol, int], float]
TemplateScatterPaytable = Dict[int, float]


def build_machine_from_composition(
    composition: Composition,
    template_paytable: TemplatePaytable,
    template_scatter_paytable: TemplateScatterPaytable,
    paylines: List[Payline],
    num_reels: int,
    num_rows: int,
) -> SlotMachine:
    strip: List[Symbol] = []
    for symbol, count in composition.items():
        strip.extend([symbol] * count)
    reels = [ReelStrip(list(strip)) for _ in range(num_reels)]
    reel_set = ReelSet(reels, num_rows=num_rows)
    paytable = Paytable(dict(template_paytable), dict(template_scatter_paytable))
    return SlotMachine(reel_set, paylines, paytable)


def scaled_paytable(paytable: Paytable, scale: float) -> Paytable:
    payouts = {key: value * scale for key, value in paytable.payouts.items()}
    scatter_payouts = {key: value * scale for key, value in paytable.scatter_payouts.items()}
    return Paytable(payouts, scatter_payouts)


def rescale_batch_for_target_rtp(batch: SpinBatch, target_rtp: float) -> Tuple[SpinBatch, float]:
    """Rescale every payout in the batch by a constant so RTP hits the target
    exactly, without re-simulating. Valid because scaling every payout by c
    multiplies mean and std dev by c but leaves their ratio (coefficient of
    variation), skewness, kurtosis, and hit frequency all unchanged, a
    spin that paid something before still pays something after."""
    raw_rtp = sum(batch.payouts) / (batch.num_spins * batch.bet)
    if raw_rtp <= 0:
        raise ValueError("cannot rescale a batch with zero or negative RTP")

    scale = target_rtp / raw_rtp
    rescaled = SpinBatch(bet=batch.bet)
    rescaled.payouts = [payout * scale for payout in batch.payouts]
    rescaled.scatter_counts = batch.scatter_counts
    rescaled.symbol_counts = batch.symbol_counts
    return rescaled, scale


@dataclass
class CandidateEvaluation:
    composition: Composition
    scale: float
    stats: GameStatistics


def evaluate_composition(
    composition: Composition,
    template_paytable: TemplatePaytable,
    template_scatter_paytable: TemplateScatterPaytable,
    paylines: List[Payline],
    target_rtp: float,
    num_reels: int,
    num_rows: int,
    num_spins: int,
    rng: random.Random,
) -> CandidateEvaluation:
    machine = build_machine_from_composition(
        composition, template_paytable, template_scatter_paytable, paylines, num_reels, num_rows
    )
    batch = run_spins(machine, num_spins, bet=1.0, rng=rng)
    rescaled_batch, scale = rescale_batch_for_target_rtp(batch, target_rtp)
    stats = compute_statistics(rescaled_batch)
    return CandidateEvaluation(composition=dict(composition), scale=scale, stats=stats)


def fitness(stats: GameStatistics, target_hit_frequency: float, target_cv: float) -> float:
    hit_error = (stats.hit_frequency - target_hit_frequency) / target_hit_frequency
    cv_error = (stats.coefficient_of_variation - target_cv) / target_cv
    return hit_error**2 + cv_error**2


def perturb_composition(composition: Composition, rng: random.Random, min_count: int = 1) -> Composition:
    """Move one unit from a randomly chosen donor symbol (above the floor)
    to a randomly chosen receiver symbol, keeping the strip length fixed."""
    symbols = list(composition.keys())
    donor_candidates = [s for s in symbols if composition[s] > min_count]
    donor = rng.choice(donor_candidates)
    receiver = rng.choice([s for s in symbols if s != donor])

    new_composition = dict(composition)
    new_composition[donor] -= 1
    new_composition[receiver] += 1
    return new_composition


def random_composition(template: Composition, rng: random.Random, min_count: int = 1) -> Composition:
    symbols = list(template.keys())
    total = sum(template.values())
    counts = {symbol: min_count for symbol in symbols}
    remaining = total - min_count * len(symbols)
    for _ in range(remaining):
        counts[rng.choice(symbols)] += 1
    return counts


@dataclass
class OptimizationResult:
    best_composition: Composition
    best_scale: float
    best_stats: GameStatistics
    best_fitness: float
    history: List[Tuple[int, float]]


def optimize_composition(
    seed_composition: Composition,
    template_paytable: TemplatePaytable,
    template_scatter_paytable: TemplateScatterPaytable,
    paylines: List[Payline],
    target_rtp: float,
    target_hit_frequency: float,
    target_cv: float,
    num_reels: int,
    num_rows: int,
    search_spins: int = 30_000,
    iterations_per_restart: int = 50,
    restarts: int = 3,
    rng: Optional[random.Random] = None,
) -> OptimizationResult:
    """Greedy hill-climbing with random restarts over reel composition space.
    RTP is corrected for free at every evaluation via rescale_batch_for_target_rtp,
    so the search only has to steer hit frequency and volatility (CV) toward target."""
    rng = rng or random.Random()

    def evaluate(comp: Composition) -> CandidateEvaluation:
        return evaluate_composition(
            comp, template_paytable, template_scatter_paytable, paylines,
            target_rtp, num_reels, num_rows, search_spins, rng,
        )

    history: List[Tuple[int, float]] = []
    best: Optional[Tuple[CandidateEvaluation, float]] = None
    eval_index = 0

    for restart in range(restarts):
        current = dict(seed_composition) if restart == 0 else random_composition(seed_composition, rng)
        current_eval = evaluate(current)
        current_fitness = fitness(current_eval.stats, target_hit_frequency, target_cv)
        history.append((eval_index, current_fitness))
        eval_index += 1
        if best is None or current_fitness < best[1]:
            best = (current_eval, current_fitness)

        for _ in range(iterations_per_restart):
            candidate = perturb_composition(current, rng)
            candidate_eval = evaluate(candidate)
            candidate_fitness = fitness(candidate_eval.stats, target_hit_frequency, target_cv)
            history.append((eval_index, candidate_fitness))
            eval_index += 1

            if candidate_fitness < current_fitness:
                current, current_fitness = candidate, candidate_fitness
                if candidate_fitness < best[1]:
                    best = (candidate_eval, candidate_fitness)

    best_eval, best_fit = best
    return OptimizationResult(
        best_composition=best_eval.composition,
        best_scale=best_eval.scale,
        best_stats=best_eval.stats,
        best_fitness=best_fit,
        history=history,
    )


def build_final_machine(
    result: OptimizationResult,
    template_paytable: TemplatePaytable,
    template_scatter_paytable: TemplateScatterPaytable,
    paylines: List[Payline],
    num_reels: int,
    num_rows: int,
) -> SlotMachine:
    machine = build_machine_from_composition(
        result.best_composition, template_paytable, template_scatter_paytable, paylines, num_reels, num_rows
    )
    machine.paytable = scaled_paytable(machine.paytable, result.best_scale)
    return machine
