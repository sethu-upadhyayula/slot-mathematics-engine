# Phase 3: Statistics Engine

`simulation/simulate.py` runs a batch of spins and collects raw payouts, scatter counts and symbol counts. `analytics/statistics.py` turns these into RTP, variance, standard deviation, skewness, kurtosis, hit frequency, percentiles, a win-size histogram and symbol frequencies, the standard outputs a game mathematician draws from a simulation run.

```
python -m scripts.run_statistics
```
