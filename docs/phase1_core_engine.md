# Phase 1: Core Engine

`SlotMachine.spin(bet)` returns a `SpinResult` containing the grid, winning lines, scatter payout and total payout. The engine has no printing or side effects, so every later analysis phase can call `spin()` in a loop and read the result.

The default config uses a 5x3 grid, 5 classic paylines, 8 symbols (4 low, 2 high, Wild and Scatter) and 20-stop reel strips. The short strips keep the machine small enough for exact enumeration in Phase 2.

```
python -m examples.run_demo
```
