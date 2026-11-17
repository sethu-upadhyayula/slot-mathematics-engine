# Probability and Math Primer

The concepts this project uses, in the order they appear, each with where it is implemented and where it is discussed further.

## Expected value, RTP and house edge

**RTP** is E[payout] / bet, the long-run average fraction of each bet returned to the player. **House edge** is 1 − RTP. Both describe the mean of the payout distribution.

- Exact: `analytics/rtp.py::exact_rtp()` enumerates every possible outcome, weights each by its probability (uniform, since every reel-stop combination is equally likely) and sums.
- Estimated: `analytics/rtp.py::monte_carlo_rtp()` samples outcomes and averages them. See [Phase 2](phase2_rtp_engine.md).

## Combinatorics and the limits of exact enumeration

The total number of reel-stop combinations is the product of the reel lengths. With 20 stops on each of 5 reels there are 3.2M combinations, and exhaustive enumeration finishes in about 20 seconds. Real machines use reel strips with 60 to 300 or more stops, which makes exhaustive enumeration infeasible (100^5 is 10 billion combinations). This is the reason Monte Carlo is needed. See [Phase 2](phase2_rtp_engine.md).

## Monte Carlo, the law of large numbers and standard error

The average of a growing number of samples converges to the true mean (the law of large numbers). The rate of convergence is governed by the standard error:

```
SE(n) = std_dev / sqrt(n)
```

Error shrinks with the square root of the sample size, so 100x more spins buys only 10x more precision. [Phase 8](phase8_simulation_suite.md) measured this directly: going from 1M to 10M spins narrowed the confidence interval by 3.14x, close to the theoretical sqrt(10) ≈ 3.16x. `notebooks/01_rtp_convergence.ipynb` visualizes the convergence.

## Confidence intervals

A 95% confidence interval on an RTP estimate is `estimate ± 1.96 * SE(n)`, where 1.96 is the 97.5th percentile of the standard normal distribution (`scipy.stats.norm.ppf(0.975)` in `simulation/streaming.py`). This follows from the central limit theorem: the sampling distribution of a mean over enough independent draws is approximately normal, whatever the shape of the underlying payout distribution, which here is far from normal (see skewness and kurtosis below).

## Variance, standard deviation and coefficient of variation

- **Variance** is E[(X − mean)²], the average squared deviation from the mean.
- **Standard deviation** is sqrt(variance), in the same units as the payout.
- **Coefficient of variation (CV)** is std_dev / mean, a scale-free measure of volatility. CV allows games with different RTPs to be compared on volatility, which raw standard deviation does not.

CV, skewness and kurtosis are invariant when every payout is scaled by the same constant, as proven in `tests/test_optimizer.py::test_rescale_preserves_hit_frequency_and_coefficient_of_variation`. This property is the basis of the [Phase 6 optimizer](phase6_optimizer.md): RTP can be corrected by rescaling without affecting hit frequency or volatility.

## Skewness and kurtosis

The normalized third and fourth moments:

```
skewness  = E[(X - mean)^3] / std_dev^3
kurtosis  = E[(X - mean)^4] / std_dev^4 - 3   (excess kurtosis; subtracting 3 makes a normal distribution read as 0)
```

Skewness measures asymmetry, and a long right tail of rare large wins produces high positive skewness. Kurtosis measures how heavy the tails are relative to a normal distribution. In [Phase 4](phase4_volatility_analysis.md), Machine B's skewness (88) and kurtosis (15,925) against Machine A's (3.7 and 28) were the clearest numerical signal of rare large wins versus frequent small wins, much clearer than hit frequency, which was actually higher for the more volatile machine.

## Statistical fairness tests (Phase 9)

Three tests, each blind to a different kind of defect:

- **Chi-square goodness of fit**: are outcomes spread evenly across categories? Blind to order.
- **Kolmogorov-Smirnov**: does the empirical distribution match a theoretical one, here the uniform distribution? Also blind to order.
- **Wald-Wolfowitz runs test**: are consecutive outcomes independent? Implemented directly in `analytics/rng_fairness.py`, since it is a single closed-form formula. Given `n1` and `n2` outcomes of each kind, the expected number of runs is `2*n1*n2/n + 1`, with a known variance, tested with a z-score against the normal distribution.

[Phase 9](phase9_rng_validation.md) found a concrete case where this matters. A weak LCG passed both chi-square and KS but failed the runs test outright, showing that no single test catches every kind of non-randomness and explaining why certification runs a full battery.

## Welford's online algorithm

Mean and variance can be computed without storing every sample:

```
n += 1
delta = x - mean
mean += delta / n
delta2 = x - mean
M2 += delta * delta2
variance = M2 / n
```

Memory use is O(1) regardless of the number of samples. The algorithm is implemented in `simulation/streaming.py::StreamingStats` and verified exactly against a naive batch computation in `tests/test_streaming.py`. It makes runs of 10M to 100M+ spins feasible in memory. See [Phase 8](phase8_simulation_suite.md) for the measured savings, over 3,000x less memory than storing every spin.
