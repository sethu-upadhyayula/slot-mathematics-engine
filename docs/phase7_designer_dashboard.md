# Phase 7: Designer Dashboard

An internal design tool rather than a player-facing interface. Sliders control reel composition and payout scale, and RTP, hit frequency, volatility and histograms update live.

## Choice of framework

`webapp/`, the player-facing game, needs a spin animation and game feel, which suits hand-written HTML, CSS and JavaScript. The dashboard needs numbers and charts that react to widget input with no game presentation, which is what Streamlit is designed for, and it avoids building a second custom frontend.

## Features

`dashboard/app.py` provides:

- Eight sliders, one per symbol, controlling how many of that symbol appear on each reel (all five reels share the same composition). The reel length is the sum of these counts rather than a fixed 20.
- A payout scale slider, exposing the RTP scaling from Phase 6 directly so that RTP can be seen moving independently of hit frequency and CV.
- A Monte Carlo batch (5,000 to 200,000 spins, selectable) that re-runs on every change through the same `build_machine_from_composition` and `compute_statistics` pipeline the optimizer uses. Results are cached by input, so returning to a previous combination is instant.
- A win-size histogram and symbol-frequency chart built with Altair and an explicit sort order. `st.bar_chart` alone sorts categorical axes alphabetically, which scrambled the histogram's 0x to 100x+ ordering.
- A download button that exports the current design as a config JSON, reusing `engine.config.machine_to_game_config` from Phase 6.

Increasing the Wild count from 1 to 3 to 5 moved RTP from 98.7% to 254% to 479% and hit frequency from 20.6% to 31.1% to 38.9%. This shows why Wild count is such a sensitive lever: Wilds both substitute into existing lines and pay on their own.

```
streamlit run dashboard/app.py
```
