# Documentation

The documentation can be read in two ways: by phase, following the order in which the engine was built, or by topic, following a concept to wherever it is implemented.

## Start here

- [architecture.md](architecture.md): the system as a whole, covering the core `spin()` contract, the config-driven design, payout scale as an independent control that recurs across four phases, and why bonus features compose with the base evaluator instead of modifying it.
- [probability_primer.md](probability_primer.md): every mathematical concept used in the project (EV, RTP, variance, CV, skewness and kurtosis, confidence intervals, chi-square, KS and runs tests, Welford's algorithm), each with a short explanation and a pointer to its implementation.

## By phase

1. [Core Engine](phase1_core_engine.md): reels, paylines, wilds, scatters and the evaluator
2. [RTP Engine](phase2_rtp_engine.md): exact enumeration vs. Monte Carlo
3. [Statistics Engine](phase3_statistics_engine.md): variance, hit frequency and histograms
4. [Volatility Analysis](phase4_volatility_analysis.md): the same RTP with a different feel
5. [Bonus Features](phase5_bonus_features.md): free spins, sticky and expanding wilds, cascades and retriggers
6. [Optimizer](phase6_optimizer.md): automatic tuning of reel composition and paytable scale to targets
7. [Designer Dashboard](phase7_designer_dashboard.md): live sliders with results that update in real time
8. [Simulation Suite](phase8_simulation_suite.md): O(1)-memory streaming statistics, confidence intervals and runtime and memory benchmarks
9. [RNG Validation](phase9_rng_validation.md): chi-square, KS and runs tests, with a negative control that the tests must catch

## By topic

- **RTP and house edge**: [phase 2](phase2_rtp_engine.md), [primer](probability_primer.md#expected-value-rtp-house-edge)
- **Monte Carlo, convergence and confidence intervals**: [phase 2](phase2_rtp_engine.md), [phase 8](phase8_simulation_suite.md), [primer](probability_primer.md#monte-carlo-the-law-of-large-numbers-and-standard-error), `notebooks/01_rtp_convergence.ipynb`
- **Variance, volatility, skewness and kurtosis**: [phase 4](phase4_volatility_analysis.md), [primer](probability_primer.md#skewness-and-kurtosis), `notebooks/02_volatility_comparison.ipynb`
- **Wild and Scatter mechanics** (substitution, expansion, sticky wilds, scatter pays, bonus triggers and retriggers): [wild_and_scatter_mechanics.md](wild_and_scatter_mechanics.md)
- **Free spins and bonus rounds**: [phase 5](phase5_bonus_features.md), [wild_and_scatter_mechanics.md](wild_and_scatter_mechanics.md#scatter)
- **Optimization and search**: [phase 6](phase6_optimizer.md), `notebooks/03_wild_count_parameter_sweep.ipynb`
- **RNG fairness and statistical testing**: [phase 9](phase9_rng_validation.md), [primer](probability_primer.md#statistical-fairness-tests-phase-9)
- **Memory-efficient simulation (Welford's algorithm)**: [phase 8](phase8_simulation_suite.md), [primer](probability_primer.md#welfords-online-algorithm)
- **Architecture**: [architecture.md](architecture.md)
- **Limitations and possible extensions**: [future_work.md](future_work.md)

## Interfaces

- `webapp/`: play the machine in a browser (Flask and vanilla JavaScript)
- `dashboard/`: design tool with sliders for inputs and RTP and volatility as outputs (Streamlit)
- `notebooks/`: pre-executed visual analysis of specific findings
- `scripts/`: the analysis tools that produced every number in the phase documents
- `examples/`: minimal usage snippets that show the API in action

See the root [README.md](../README.md) for how to run each of these.
