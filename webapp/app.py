from pathlib import Path

from flask import Flask, jsonify, render_template, request

from engine.config import load_game_config
from engine.features.free_spins import FreeSpinsConfig, play_round
from webapp.serialize import serialize_round_result

REPO_ROOT = Path(__file__).resolve().parent.parent

app = Flask(__name__)

MACHINE = load_game_config(str(REPO_ROOT / "configs" / "full_game_with_bonus.json"))
BONUS_CONFIG = FreeSpinsConfig(
    trigger_scatter_count=3,
    spins_awarded=10,
    retrigger_scatter_count=3,
    retrigger_spins_awarded=5,
    sticky_wilds=True,
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/spin", methods=["POST"])
def spin():
    data = request.get_json(silent=True) or {}
    try:
        bet = float(data.get("bet", 1.0))
    except (TypeError, ValueError):
        return jsonify({"error": "bet must be a number"}), 400

    if bet <= 0:
        return jsonify({"error": "bet must be positive"}), 400

    result = play_round(MACHINE, BONUS_CONFIG, bet=bet)
    return jsonify(serialize_round_result(result))


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
