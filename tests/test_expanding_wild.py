from engine.features.expanding_wild import apply_expanding_wilds
from engine.symbols import Symbol


def test_reel_with_wild_expands_to_fill_the_column():
    grid = [
        [Symbol.CHERRY, Symbol.WILD, Symbol.PLUM],
        [Symbol.ORANGE, Symbol.BAR, Symbol.SEVEN],
    ]

    expanded = apply_expanding_wilds(grid)

    assert expanded[0] == [Symbol.WILD, Symbol.WILD, Symbol.WILD]
    assert expanded[1] == [Symbol.ORANGE, Symbol.BAR, Symbol.SEVEN]


def test_grid_with_no_wilds_is_unchanged():
    grid = [
        [Symbol.CHERRY, Symbol.LEMON],
        [Symbol.ORANGE, Symbol.PLUM],
    ]

    expanded = apply_expanding_wilds(grid)

    assert expanded == grid
