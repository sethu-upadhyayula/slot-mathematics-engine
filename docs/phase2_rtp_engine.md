# Phase 2: RTP Engine

`analytics/rtp.py` computes RTP in two ways. `exact_rtp()` enumerates all reel-stop combinations (3.2M for the default config) and `monte_carlo_rtp()` samples spins. `tests/test_rtp.py` verifies them against each other and against a small machine whose RTP can be computed by hand.

The default paytable was first set without checking the math and produced an RTP of 335.69%, far above anything a real machine would ship with. Because RTP scales linearly with the paytable multipliers for a fixed reel and payline structure, the paytable was rescaled by a single constant factor to reach 98.98%.

```
python -m scripts.run_rtp
```

`notebooks/01_rtp_convergence.ipynb` plots the convergence funnel that this script reports as text.
