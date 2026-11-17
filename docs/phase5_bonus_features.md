# Phase 5: Bonus Features

`engine/features/` adds the bonus mechanics as independent, composable pieces rather than a single monolithic bonus mode:

- `expanding_wild.py`: a Wild landing anywhere on a reel fills the whole reel for that spin.
- `cascade.py`: winning symbols are removed, the remaining symbols drop down, new symbols refill from the top (drawn from that reel's own symbol distribution), and the grid is re-evaluated until no win remains. The payout multiplier increases with each successive cascade.
- `free_spins.py`: `play_round()` is the top-level entry point, used in place of `machine.spin()`. It plays a base spin and, if enough scatters land, plays a free spins round with optional sticky wilds (which accumulate and persist for the rest of the round) and retriggers (additional scatters during free spins extend the round).

Each mechanic has unit tests built on deterministic reels and grids, so the core bookkeeping (removal and refill positions, sticky wild persistence and retrigger accounting) is verified without depending on random outcomes.

## Finding: bonus features change RTP, not only the feel of the game

Adding sticky-wild free spins to the already tuned paytable in `default_game.json` pushed total RTP to about 395%, because that paytable was balanced only for a single base-game spin. `configs/full_game_with_bonus.json` uses the same reels and paylines with a paytable rescaled so that RTP returns to about 96% including the bonus. This was confirmed by Monte Carlo, since exact enumeration becomes infeasible once a bonus round can vary in length. In the final breakdown, 25.2% of total RTP comes from the base game and 74.8% from the free spins bonus, the kind of RTP-by-feature breakdown that appears on a real PAR sheet.

```
python -m examples.run_bonus_demo   # each mechanic triggering on a live spin
python -m scripts.run_bonus_rtp     # RTP contribution of the base game vs. the bonus feature
```
