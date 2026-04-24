import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_event_1_scene_loads():
    scene = json.loads((ROOT / "data/dl1/scenes/event_1_ambush.json").read_text())
    assert scene["scene_id"] == "DL1_EVENT_1_AMBUSH"
    assert scene["npc_scripts"]["NPC_TOEDE"] == "demand_staff_then_flee"
    assert any(e["actor_id"] == "HOBGOBLIN_EVENT1" for e in scene["enemy_roster"])
