# Phase 8: Simulation Suite

The simulation suite runs the engine at 1M, 10M and 100M spins and reports confidence intervals, convergence, runtime and memory usage.

`notebooks/01_rtp_convergence.ipynb` already covers convergence visually. This phase adds a proper confidence interval on the RTP estimate and, more importantly, measures memory usage alongside runtime.

## Batch storage does not scale to 100M spins

The Monte Carlo code in earlier phases (`run_spins` in `simulation/simulate.py`) returns a `SpinBatch` holding a Python list of every payout and scatter count from every spin. That works at 2M spins, but at 100M spins a Python list of floats alone costs several gigabytes, so storing raw data becomes the bottleneck rather than computing statistics.

`simulation/streaming.py` solves this with `StreamingStats`, a running accumulator based on Welford's online algorithm for mean and variance. It processes one spin at a time and updates a fixed set of values (mean, running sum of squared deviations, hit count and maximum payout) without storing per-spin history, so memory use is O(1) in the number of spins. `tests/test_streaming.py` verifies exact agreement with a naive batch computation, and `tracemalloc` measures the memory difference:

```
       Spins    Batch peak (MB)    Streaming peak (MB)      Ratio
-----------------------------------------------------------------
     100,000                4.0                   0.01       746x
     500,000               20.3                   0.01      3706x
```

Batch memory grows linearly with spin count, while streaming memory stays flat. The widening ratio is the O(n) vs. O(1) difference made visible. The exact ratios depend on the Python version and platform, and at 500,000 spins they consistently exceed 3,000x.

## Runtime, throughput and confidence intervals

```
       Spins  Runtime (s)      Spins/sec   RTP estimate                   95% CI
--------------------------------------------------------------------------------
   1,000,000          9.4        106,227       98.7680%     [98.2950%, 99.2410%]
  10,000,000        106.4         93,943       99.0352%     [98.8847%, 99.1858%]
```

The exact RTP from Phase 2 (98.9785%) falls inside both intervals. The interval width shrank from about 0.946 to about 0.301 percentage points between 1M and 10M spins, a 3.14x reduction that closely matches the theoretical √10 ≈ 3.16x implied by `SE = std_dev/sqrt(n)`.

## Throughput at 100M spins

At the measured 95,000 to 106,000 spins per second, 100M spins would take an estimated 17.7 minutes, so that run is reported as an estimate rather than executed. `StreamingStats` solves the memory side of scaling to certification-grade spin counts (100M or more is standard for RTP certification), but pure Python's per-spin overhead remains the throughput bottleneck. Running 100M+ spins in reasonable time would require a vectorized engine that generates reel stops and evaluates wins across NumPy arrays, or a compiled extension in Rust or C.

```
python -m scripts.run_simulation_suite
```
