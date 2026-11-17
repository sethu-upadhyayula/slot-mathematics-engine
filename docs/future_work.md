# Limitations and Possible Extensions

## Engine

- **Only classic left-to-right paylines are implemented.** "Ways to win" (any position, no fixed lines) and cluster pays (connected groups of matching symbols, common in cascade games) require a different evaluation model rather than a config option.
- **All five reels share the same composition in every config.** Real machines often weight each reel differently, for example making Wild rarer on reel 1. The engine already supports this because `ReelStrip` is defined per reel, but no config uses it yet.
- **Cascades and free spins with sticky wilds are tuned separately.** A game combining all of the Phase 5 mechanics at once (cascading free spins with accumulating sticky wilds and a rising multiplier) has not been assembled or RTP-balanced as a whole. Each mechanic's demo config exercises it independently.

## Performance

- **Pure Python reaches about 100,000 spins per second** (Phase 8). A 100M-spin run, the standard for RTP certification, would take an estimated 17 to 18 minutes. This limit is architectural. Reaching it would require a vectorized engine (NumPy batch simulation that generates and evaluates many spins as array operations) or a compiled extension in Rust or C. `StreamingStats` addresses the memory side of scaling to that spin count, but not throughput.

## Optimization

- **The Phase 6 optimizer uses greedy hill climbing with random restarts**, which does not guarantee a global optimum. It landed close to its targets (hit frequency of 33.5% against a 30% target) but not exactly on them. Simulated annealing, genetic algorithms or gradient-free methods such as CMA-ES would likely converge more tightly at the cost of added complexity.
- **The optimizer searches only uniform reel composition**, with the same mix on all five reels. With per-reel weighting, the full search space is much larger than what is currently explored.

## RNG validation

- **Three tests rather than a full battery.** Certification suites such as NIST SP 800-22 and TestU01 run dozens of tests aimed at different failure modes. Phase 9 uses three tests that are each instructive and practical to implement directly.

## Documentation

- **There is no PAR-sheet export.** Slot math teams produce a standardized PAR sheet for regulators that lists every symbol weight, paytable value and calculated RTP, hit-frequency and volatility figure. `machine_to_game_config()` captures the raw data, but nothing yet renders it as a readable report.
