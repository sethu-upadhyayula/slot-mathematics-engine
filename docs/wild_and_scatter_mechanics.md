# Wild and Scatter Mechanics

Wild and Scatter receive special treatment throughout the evaluator and feature code. This document brings that logic together, since in the source it is spread across `engine/evaluator.py` (Phase 1) and `engine/features/` (Phase 5).

## Wild

**Substitution** (`engine/evaluator.py::evaluate_payline`): reading a payline from left to right, Wild matches whichever symbol the line is paying as. If the leftmost symbol is Wild, the paying symbol is the first non-Wild symbol encountered. A line of `WILD, WILD, CHERRY, CHERRY, ORANGE` therefore pays as 4x CHERRY (the Wilds extend the match, which breaks at ORANGE), not as a 2-symbol Wild match. If every symbol on the line is Wild, it pays according to Wild's own paytable entry.

**Wild pays on its own**: `WILD` has its own paytable entries (for example `(Symbol.WILD, 5): 140` in `configs/default_game.json`), so three or more Wilds in a row pay independently of substitution. This is why Wild count is such a sensitive lever for RTP: Wilds both substitute into other lines, raising their hit rate, and pay for themselves. `notebooks/03_wild_count_parameter_sweep.ipynb` measures this directly, with raw RTP rising from 57% to 1215% as the Wild count goes from 0 to 6 per reel and everything else held fixed.

**Wild does not substitute for Scatter**: scatters are excluded from payline evaluation entirely (see below), so a Wild never needs to count as a Scatter.

**Expanding Wild** (`engine/features/expanding_wild.py`): a Wild landing anywhere in a reel's visible window turns the entire reel Wild for that spin. This is applied as a grid transformation before evaluation, so the base evaluator never needs to know that expansion happened.

**Sticky Wild** (`engine/features/free_spins.py::_apply_sticky_wilds`): applies only within a free spins round. Each Wild that lands is recorded by grid position, and on every later spin in the round those positions are forced to Wild before evaluation, regardless of what the reel actually shows. Wilds only accumulate, so a round can end with more forced Wild positions than it started with but never fewer.

## Scatter

**Excluded from payline evaluation**: `evaluate_payline` returns `None` immediately if the leftmost symbol on a line is Scatter, so scatters never form or extend a payline win.

**Pays by count, not position** (`engine/evaluator.py::evaluate_scatter`): the scatter payout depends only on how many Scatter symbols appear anywhere in the grid, summed across all reels and rows. It is looked up in a separate `scatter_paytable` keyed by count, independent of the paylines and of where the scatters landed.

**Triggers free spins** (`engine/features/free_spins.py::count_scatters` and `FreeSpinsConfig.trigger_scatter_count`): a base spin whose scatter count meets the threshold starts a free spins round through `play_round()`. This is separate from the scatter cash payout above, and a real game, like `configs/default_game.json`, can pay a direct scatter win and trigger the bonus on the same spin.

**Retriggers**: the same threshold check runs on every spin during a free spins round, and meeting it again extends the round by `retrigger_spins_awarded` spins (`run_free_spins()`). For the expected round length to remain finite, `P(retrigger) * retrigger_spins_awarded` must stay below 1, the same extinction condition that governs a branching process. `tests/test_free_spins.py` includes a case with `retrigger_spins_awarded=0` that guarantees termination regardless of trigger probability.
