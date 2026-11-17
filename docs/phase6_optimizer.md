# Phase 6: Optimizer

The optimizer takes a target RTP, a target hit frequency and a target volatility (coefficient of variation), and produces a reel composition and paytable scale that meet all three, saved as a reusable config.

## Why the problem is tractable

Scaling every paytable multiplier by a constant `c` scales RTP by exactly `c` but leaves several statistics exactly unchanged:

- **Hit frequency**: whether a spin pays at all does not depend on how much it pays.
- **Coefficient of variation, skewness and kurtosis**: these are normalized moments, so scaling multiplies the numerator and denominator by the same factor.

`tests/test_optimizer.py::test_rescale_preserves_hit_frequency_and_coefficient_of_variation` and `test_paytable_scaling_scales_exact_rtp_linearly` prove this directly.

In practice, RTP can be corrected at every step of the search without re-simulating: run a batch, measure the raw RTP and rescale every payout by `target_rtp / raw_rtp`. The search only needs to find a reel composition with the right hit frequency and volatility, and RTP follows.

## The search

`analytics/optimizer.py` implements greedy hill climbing with random restarts over reel compositions, meaning how many of each symbol appear on a reel with the total reel length held fixed. Each step moves one unit from a random donor symbol to a random receiver symbol, evaluates the result with a 30,000-spin Monte Carlo batch (fast and noisy, which is adequate for steering), and keeps the move if the fitness improves. Fitness is the weighted squared error against the target hit frequency and CV.

Once the search settles, the scale from the last noisy batch is not precise enough for a final RTP figure, so `scripts/run_optimizer.py` recalibrates the scale with `exact_rtp()`. The 20-stop reel strips are still short enough for exhaustive enumeration in this one-time precision pass.

## Result

The targets were 96% RTP, 30% hit frequency and a CV of 2.5, a medium volatility between the low-volatility (about 1.9) and high-volatility (about 3.7) machines from Phase 4. The search evaluated 153 compositions in about 55 seconds and reached a hit frequency of 33.5% and a CV of 2.503. Hit frequency is close to target and volatility essentially exact, which is reasonable for a heuristic search without a guaranteed global optimum. After exact recalibration, RTP is precisely 96.0000%. The result is written to `configs/optimized_game.json`.

```
python -m scripts.run_optimizer
```

`notebooks/03_wild_count_parameter_sweep.ipynb` varies one symbol by hand and plots raw RTP separately from hit frequency and CV, a one-dimensional view of what this search does automatically across all 8 symbols.
