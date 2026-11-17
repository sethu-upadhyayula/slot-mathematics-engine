from engine.config import load_game_config, load_template_paytable, machine_to_game_config
from engine.symbols import Symbol


def test_load_game_config_builds_a_working_machine():
    machine = load_game_config("configs/default_game.json")

    assert machine.reel_set.num_reels == 5
    assert machine.reel_set.num_rows == 3
    assert len(machine.paylines) == 5
    assert machine.paytable.payout_for(Symbol.CHERRY, 3) is not None


def test_machine_to_game_config_round_trips_through_json(tmp_path):
    machine = load_game_config("configs/default_game.json")

    config = machine_to_game_config(machine, description="round trip test")
    out_path = tmp_path / "roundtrip.json"
    import json

    out_path.write_text(json.dumps(config))

    reloaded = load_game_config(str(out_path))

    assert reloaded.reel_set.num_reels == machine.reel_set.num_reels
    assert reloaded.paylines == machine.paylines
    assert reloaded.paytable.payout_for(Symbol.CHERRY, 3) == machine.paytable.payout_for(Symbol.CHERRY, 3)


def test_load_template_paytable_matches_load_game_config():
    machine = load_game_config("configs/default_game.json")
    paylines, template_paytable, template_scatter_paytable = load_template_paytable("configs/default_game.json")

    assert paylines == machine.paylines
    assert template_paytable == machine.paytable.payouts
    assert template_scatter_paytable == machine.paytable.scatter_payouts
