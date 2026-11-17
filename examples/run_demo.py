from engine.config import load_game_config
from engine.display import format_grid


def main() -> None:
    machine = load_game_config("configs/default_game.json")
    result = machine.spin(bet=1.0)

    print("Grid:")
    print(format_grid(result.grid))
    print()
    print(f"Total payout: {result.total_payout}")
    print(f"Scatter payout: {result.scatter_payout}")
    print(f"Winning lines: {len(result.win_lines)}")
    for win in result.win_lines:
        print(f"  Payline {win.payline_index}: {win.match_count}x {win.symbol.value} -> {win.payout}")


if __name__ == "__main__":
    main()
