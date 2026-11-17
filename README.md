# Slot Mathematics Engine

An analysis platform for casino slot game mathematics, built on a single core engine. It covers reel mechanics, RTP, Monte Carlo simulation, volatility analysis, bonus feature math, automated game tuning and RNG validation.

## Structure

```
engine/       core simulator (reels, symbols, paylines, paytable, evaluator, features/)
analytics/    RTP, statistics, optimizer, RNG fairness tests and reporting
simulation/   batch spin running and O(1)-memory streaming statistics
configs/      game definitions (reel strips, paytable, paylines) as JSON
tests/        unit tests, each verified against a hand-computable case
examples/     usage snippets (a single spin, each bonus mechanic triggering)
scripts/      analysis tools that produce the reported results for each phase
notebooks/    visual analysis of results from the phase reports
docs/         phase write-ups and topic references (architecture, math primer, mechanics)
webapp/       Flask and vanilla JavaScript interface for playing the machine in a browser
dashboard/    Streamlit designer dashboard with sliders for inputs and RTP and volatility as outputs
```

## Documentation

[docs/README.md](docs/README.md) is the best starting point for understanding the material. It indexes everything by phase and by topic (RTP, volatility, wild and scatter mechanics, RNG fairness and more), and links to [docs/architecture.md](docs/architecture.md), which explains how the system fits together, and [docs/probability_primer.md](docs/probability_primer.md), which covers every mathematical concept used.

## Phases

1. [Core Engine](docs/phase1_core_engine.md): reels, paylines, wilds, scatters and the evaluator
2. [RTP Engine](docs/phase2_rtp_engine.md): exact enumeration over 3.2M reel-stop combinations vs. Monte Carlo
3. [Statistics Engine](docs/phase3_statistics_engine.md): variance, hit frequency and histograms
4. [Volatility Analysis](docs/phase4_volatility_analysis.md): the same RTP with a different feel
5. [Bonus Features](docs/phase5_bonus_features.md): free spins, sticky and expanding wilds, cascades and retriggers
6. [Optimizer](docs/phase6_optimizer.md): automatic tuning of reel composition and paytable scale to a target RTP, hit frequency and volatility, reaching 96.00% RTP against a 96% target
7. [Designer Dashboard](docs/phase7_designer_dashboard.md): live sliders for reel composition and payout scale, with RTP and volatility updating in real time
8. [Simulation Suite](docs/phase8_simulation_suite.md): O(1)-memory streaming statistics using over 3,000x less memory than batch storage, plus confidence intervals and runtime benchmarks
9. [RNG Validation](docs/phase9_rng_validation.md): chi-square, KS and runs tests across 4 standard generators and a weak generator used as a negative control

Each document describes what was built and, where relevant, which results came out wrong at first and why.

## Running it

Examples:

```
python -m examples.run_demo          # one base-game spin
python -m examples.run_bonus_demo    # each bonus mechanic triggering on a live spin
```

Analysis scripts:

```
python -m scripts.run_rtp                      # exact vs. Monte Carlo RTP
python -m scripts.run_statistics               # full statistics report over 2M spins
python -m scripts.run_volatility_comparison    # low vs. high volatility at the same RTP
python -m scripts.run_bonus_rtp                # RTP contribution of the base game vs. the bonus
python -m scripts.run_optimizer                # tune to a target RTP, hit frequency and volatility
python -m scripts.run_rng_validation           # chi-square, KS and runs tests across 5 generators
python -m scripts.run_simulation_suite         # streaming statistics, confidence intervals, runtime and memory benchmarks
```

```
python -m pytest tests/ -v    # 48 tests, each verified against a hand-computed case
```

Run everything with `-m` from the repository root (not, for example, `python examples/run_demo.py`) so that `engine`, `analytics` and `simulation` are importable. Running a script directly adds only its own folder to the import path.

## Playing it

```
python -m webapp.app
```

Then open http://127.0.0.1:5000. The interface includes a spin animation, a credit balance, highlighting of winning paylines, and full free spins rounds with sticky wilds that play out spin by spin. It runs on `configs/full_game_with_bonus.json`, the config whose paytable is balanced to about 96% RTP including the bonus. The backend is a single `/api/spin` endpoint that calls `engine.features.free_spins.play_round()` and returns the whole round (the base spin plus any triggered free spins) as JSON. The frontend contains no game logic and only renders what the engine returns.

## Designing it

```
streamlit run dashboard/app.py
```

Then open http://localhost:8501. This is the internal design counterpart to `webapp/`. It has no game presentation, only sliders for reel composition and payout scale, with RTP, hit frequency, volatility (standard deviation, CV and skewness) and a win-size histogram updating live. It uses the same pipeline as the Phase 6 optimizer (`build_machine_from_composition`, then Monte Carlo, then `compute_statistics`), driven by a person instead of a search algorithm. A button downloads the current design as a config JSON.

## Visualizing it

```
python -m jupyter notebook notebooks/
```

Three notebooks turn results from the phase reports into charts:

- `01_rtp_convergence.ipynb`: plots the Monte Carlo convergence funnel (the running RTP estimate against spin count on a log scale) against a theoretical shrinking confidence band.
- `02_volatility_comparison.ipynb`: overlays the win-size distributions of Machines A and B on a log-log histogram and breaks hit frequency down into no win, sub-bet win and real win. This makes the Phase 4 finding visible: most of Machine B's higher hit rate comes from sub-bet consolation wins.
- `03_wild_count_parameter_sweep.ipynb`: varies the Wild count and plots raw RTP, which rises sharply, separately from hit frequency and CV, which are unaffected by the Phase 6 RTP rescaling. This is a one-dimensional view of the search the Phase 6 optimizer runs across eight dimensions.

All three notebooks are pre-executed with their outputs and charts embedded, so the plots can be viewed without re-running anything. Re-running them reproduces the results exactly because each uses fixed seeds.
