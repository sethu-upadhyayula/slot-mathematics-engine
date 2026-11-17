# Phase 4: Volatility Analysis

`configs/volatility_low.json` and `configs/volatility_high.json` define two machines tuned to the same RTP of about 96% with different reel weightings and paytables. One favors frequent small wins and the other rare large wins.

```
python -m scripts.run_volatility_comparison
```

## Finding: hit frequency is a misleading proxy for volatility

A natural expectation is that a high-volatility machine hits less often. The data showed the opposite. Machine B (high volatility) had a higher hit frequency than Machine A (49.9% vs. 36.7%), because its most common filler symbol, at 40% of the reel, produces frequent small consolation wins of 0.7x to 2.8x the bet. Its volatility comes from a bimodal win-size distribution: many near-worthless hits plus a long, thin tail of very large multipliers. Machine B's skewness is 88 against 3.7, its kurtosis 15,925 against 28, and its maximum win 1,139x against 65x. This mirrors a common player complaint about high-volatility slots, that they hit often but rarely feel like a win. The shape of the win-size distribution, captured by skewness and kurtosis, measures volatility far better than hit frequency alone.

`notebooks/02_volatility_comparison.ipynb` plots the overlaid win-size histograms and the breakdown into no win, sub-bet win and real win.
