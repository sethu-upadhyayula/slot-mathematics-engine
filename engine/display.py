from engine.models import Grid


def format_grid(grid: Grid) -> str:
    num_rows = len(grid[0])
    rows = []
    for row in range(num_rows):
        rows.append(" | ".join(f"{grid[reel][row].value:^8}" for reel in range(len(grid))))
    return "\n".join(rows)
