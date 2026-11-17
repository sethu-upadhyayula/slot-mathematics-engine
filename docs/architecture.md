# Architecture

## The core contract

```python
SlotMachine.spin(bet, rng) -> SpinResult
```

`SpinResult` is a plain data object (grid, winning lines, scatter payout and total payout) with no printing or side effects. Every later phase depends on this decision from Phase 1:

```
engine/            pure mechanics: reels -> grid -> evaluate -> SpinResult
  features/        optional add-ons that compose with the base engine
simulation/        runs spin() in a loop, either in batch (stores everything) or
                   streaming (Welford's algorithm, O(1) memory)
analytics/         RTP, statistics and the optimizer, all callers of spin() and
                   run_spins() that never touch reel or evaluator internals
webapp/, dashboard/, scripts/, notebooks/   presentation layers that call analytics,
                   render results and contain no game math of their own
```

Nothing above the engine layer needs to know how a spin is computed. The RTP calculator, statistics engine, optimizer, designer dashboard and webapp all call `spin()`, or `play_round()` once bonus features exist, in a loop and read the result. As a result, the analysis phases added after Phase 1 never required changes to `engine/reels.py` or `engine/evaluator.py`.

## Config-driven design

Reel strips, paylines and paytables are stored as JSON in `configs/` and loaded by `engine/config.py`. This allows five different machines (`default_game`, `volatility_low`, `volatility_high`, `full_game_with_bonus` and `optimized_game`) without any code branching on which game is being played. `machine_to_game_config()` works in the opposite direction, serializing a machine built in code by the optimizer or the dashboard back into the same JSON format, so anything produced programmatically becomes a reusable config.

## Payout scale as an independent control

This principle appears in four phases and is worth stating once.

Scaling every paytable multiplier by a constant `c` scales RTP by exactly `c` while leaving hit frequency, coefficient of variation, skewness and kurtosis exactly unchanged, as proven in `tests/test_optimizer.py`. It was applied in the following order:

- **Phase 2**: the initial paytable produced 335.69% RTP. It was corrected by solving for a single scale factor rather than re-deriving the paytable.
- **Phase 5**: adding sticky-wild free spins to that paytable pushed RTP to about 395%, because the paytable had been balanced only for the base game. The same fix was applied to the bonus-inclusive config.
- **Phase 6**: the optimizer searches only reel composition for hit frequency and volatility. RTP is corrected analytically for every candidate through this rescaling, without re-simulating.
- **Phase 7**: the dashboard exposes payout scale as its own slider, separate from the composition sliders, so the user can see RTP move on its own axis.

Composition (which symbols appear and how often) and payout scale (how much each win pays) are independent. Composition sets the shape of the outcome distribution and scale sets its size. Confusing the two caused the RTP overshoots in Phases 2 and 5.

## Bonus features compose with the base engine

The features in `engine/features/` (expanding wilds, cascades and free spins) are functions that call the base `evaluate_spin()` or `SlotMachine.spin()` and transform the grid or repeat the call. None of them modify the evaluator:

- `apply_expanding_wilds(grid)` transforms a grid before evaluation.
- `run_cascade()` calls `evaluate_spin()` repeatedly on a progressively modified grid.
- `play_round()` calls `machine.spin()` once and then, if triggered, calls `run_free_spins()`, which calls `machine.spin()` in a loop.

None of them required editing `engine/evaluator.py`, so the correctness of the base evaluator, established by `tests/test_evaluator.py`, is unaffected by how many features are layered on top.

## Two front ends, one backend

`webapp/` (Flask and vanilla JavaScript) and `dashboard/` (Streamlit) serve different purposes. One is a player-facing game with a spin animation and the other is a design tool with sliders and live statistics. Neither contains game math. Both call the same `engine` and `analytics` functions that the scripts and notebooks use, so any correction to the underlying math needs to be made in only one place.

## Testing approach

Every module has tests, and the standard throughout is hand-computable cases rather than checks that code runs without errors. Examples include a 3-reel, 2-stop machine with a known RTP of 125% (Phase 2), a 5-spin batch with hand-calculated variance (Phase 3), and an intentionally weak RNG that the fairness tests must catch (Phase 9). All 48 tests follow this pattern.
