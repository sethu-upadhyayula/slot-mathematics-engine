# Phase 9: RNG Validation

This phase compares five random number sources. Python's `random` module and NumPy's legacy generator both implement the Mersenne Twister, so comparing them is a cross-implementation check of one algorithm rather than a comparison of two. The full set is Python's MT19937, NumPy's MT19937, NumPy's PCG64 (NumPy's modern default), NumPy's SFC64, and an intentionally weak linear congruential generator (`WeakLCG`) as a negative control. A test suite that never fails anything has not shown that it can catch a bad generator.

## Integration with the engine

The engine's reels only ever call `.randrange(n)` on the `rng` object they receive, and nothing in `engine/` imports `random` or `numpy`. `NumpyGeneratorAdapter` in `analytics/rng_fairness.py` wraps any NumPy generator to expose the same `.randrange(n)` and `.random()` interface, so it plugs into `machine.spin(rng=...)` as a true drop-in replacement.

## Three tests for three kinds of defect

- **Chi-square goodness of fit**: are `randrange(n)` draws spread evenly across all `n` categories? Detects biased frequencies.
- **Kolmogorov-Smirnov**: do `random()` draws match the continuous Uniform(0,1) distribution? Detects problems with distributional shape.
- **Runs test (Wald-Wolfowitz)**: implemented directly, since it is a single formula. Given a binary sequence, is the number of runs (maximal streaks of the same value) consistent with independence? Too few runs indicates clustering and too many indicates suspicious alternation. This test detects sequential dependence between draws, which the other two cannot see because they consider only where values land, not the order in which they arrive.

## Result

```
RNG                                  Chi2 p      KS p      Runs p
Python random (MT19937)              0.9070 PASS 0.0737 PASS 0.8150 PASS
NumPy MT19937                        0.8000 PASS 0.6665 PASS 0.8096 PASS
NumPy PCG64 (NumPy's default)        0.3609 PASS 0.0704 PASS 0.7808 PASS
NumPy SFC64                          0.2550 PASS 0.4432 PASS 0.7103 PASS
Weak LCG (negative control)          1.0000 PASS 0.9980 PASS 0.0000 FAIL
```

The weak LCG passes both chi-square and KS, because its low bits still land roughly evenly and roughly match a uniform shape, but it fails the runs test outright (p ≈ 0.0000). Chi-square and KS check only where values land. The runs test checks the order in which they arrive, which is exactly where a classic LCG's low-bit weakness appears. This is also why certification suites such as NIST SP 800-22 and TestU01 run a battery of different tests: no single test catches every kind of defect.

## Effect on the game

Plugging the same five sources into the engine (300,000 spins each on `configs/default_game.json`, with an exact RTP of 98.9785% from Phase 2):

```
RNG                                Measured RTP    Diff from exact
Python random (MT19937)                98.5780%    -0.4005%
NumPy MT19937                          98.5427%    -0.4358%
NumPy PCG64 (NumPy's default)          99.0230%    +0.0445%
NumPy SFC64                            98.7968%    -0.1817%
Weak LCG (negative control)           115.6877%   +16.7092%
```

The four sound generators land within Monte Carlo noise of the exact value. The weak LCG is off by nearly 17 percentage points, so a statistical test failure translates directly into an exploitable bias in the game. This is why casinos require certified RNGs: a biased generator does not just fail a p-value, it changes the machine's actual payout percentage.

```
python -m scripts.run_rng_validation
```
