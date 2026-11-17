import json
import random
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analytics.optimizer import build_machine_from_composition, scaled_paytable  # noqa: E402
from analytics.statistics import HISTOGRAM_BUCKETS, compute_statistics  # noqa: E402
from engine.config import load_template_paytable, machine_to_game_config  # noqa: E402
from engine.symbols import Symbol  # noqa: E402
from simulation.simulate import run_spins  # noqa: E402

st.set_page_config(page_title="Slot Math Designer Dashboard", layout="centered")
st.title("Slot Mathematics - Designer Dashboard")
st.caption(
    "Adjust reel composition and payout scale on the left; RTP, hit frequency, "
    "and volatility update live. This is a design tool, not a player-facing UI - "
    "see webapp/ for that."
)

PAYLINES, TEMPLATE_PAYTABLE, TEMPLATE_SCATTER_PAYTABLE = load_template_paytable(
    str(REPO_ROOT / "configs" / "default_game.json")
)

SYMBOLS = [
    Symbol.CHERRY,
    Symbol.LEMON,
    Symbol.ORANGE,
    Symbol.PLUM,
    Symbol.BAR,
    Symbol.SEVEN,
    Symbol.WILD,
    Symbol.SCATTER,
]
DEFAULT_COUNTS = {
    Symbol.CHERRY: 5,
    Symbol.LEMON: 4,
    Symbol.ORANGE: 3,
    Symbol.PLUM: 3,
    Symbol.BAR: 2,
    Symbol.SEVEN: 1,
    Symbol.WILD: 1,
    Symbol.SCATTER: 1,
}

st.sidebar.header("Reel Composition")
st.sidebar.caption("Count per symbol, per reel (all 5 reels identical). Reel length is whatever these sum to.")

composition = {}
for symbol in SYMBOLS:
    composition[symbol] = st.sidebar.slider(symbol.value, min_value=0, max_value=10, value=DEFAULT_COUNTS[symbol])

reel_length = sum(composition.values())
st.sidebar.metric("Reel length (stops)", reel_length)

st.sidebar.header("Payout Scale")
st.sidebar.caption("Uniformly scales every paytable multiplier - the 'free RTP dial' from Phase 6.")
payout_scale = st.sidebar.slider("Scale", min_value=0.05, max_value=3.0, value=1.0, step=0.05)

st.sidebar.header("Simulation")
num_spins = st.sidebar.select_slider(
    "Sample size (larger = slower, less noisy)", options=[5_000, 20_000, 50_000, 200_000], value=20_000
)

non_scatter_total = sum(count for symbol, count in composition.items() if symbol != Symbol.SCATTER)
if non_scatter_total == 0:
    st.error("At least one non-scatter symbol needs a nonzero count.")
    st.stop()


@st.cache_data(show_spinner="Simulating...")
def evaluate(composition_items, scale, spins, seed=42):
    comp = {Symbol(name): count for name, count in composition_items}
    machine = build_machine_from_composition(
        comp, TEMPLATE_PAYTABLE, TEMPLATE_SCATTER_PAYTABLE, PAYLINES, num_reels=5, num_rows=3
    )
    machine.paytable = scaled_paytable(machine.paytable, scale)
    batch = run_spins(machine, spins, bet=1.0, rng=random.Random(seed))
    return compute_statistics(batch), machine


composition_items = tuple(sorted((symbol.value, count) for symbol, count in composition.items()))
stats, machine = evaluate(composition_items, payout_scale, num_spins)

col1, col2, col3, col4 = st.columns(4)
col1.metric("RTP", f"{stats.rtp:.2%}")
col2.metric("Hit Frequency", f"{stats.hit_frequency:.2%}")
col3.metric("Std Dev", f"{stats.std_dev:.2f}")
col4.metric("Scatter Trigger Freq", f"{stats.scatter_trigger_frequency:.2%}")

col5, col6, col7 = st.columns(3)
col5.metric("Coefficient of Variation", f"{stats.coefficient_of_variation:.2f}")
col6.metric("Skewness", f"{stats.skewness:.2f}")
col7.metric("Max Win", f"{stats.max_win_multiplier:.1f}x")

st.subheader("Win Size Histogram")
bucket_order = [label for label, _, _ in HISTOGRAM_BUCKETS]
histogram_df = pd.DataFrame(
    {"bucket": list(stats.win_histogram.keys()), "spins": list(stats.win_histogram.values())}
)
histogram_chart = (
    alt.Chart(histogram_df)
    .mark_bar()
    .encode(x=alt.X("bucket", sort=bucket_order, title="Win size"), y=alt.Y("spins", title="Spins"))
)
st.altair_chart(histogram_chart, use_container_width=True)

st.subheader("Symbol Frequency")
symbol_series = pd.Series(stats.symbol_frequency).sort_values(ascending=False)
st.bar_chart(symbol_series)

st.caption(
    f"Based on a {num_spins:,}-spin Monte Carlo sample, re-simulated automatically whenever an "
    "input changes (and cached, so revisiting the same combination is instant). This is "
    "sampling, not exact enumeration - expect visible noise on rare-event stats like "
    "scatter trigger frequency, especially at the smaller sample sizes."
)

st.divider()
config_json = machine_to_game_config(
    machine, description="Exported from the designer dashboard (dashboard/app.py)."
)

st.download_button(
    "Download this configuration as JSON",
    data=json.dumps(config_json, indent=2),
    file_name="dashboard_config.json",
    mime="application/json",
)
