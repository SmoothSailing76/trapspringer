from trapspringer.engine.orchestrator import Orchestrator
from trapspringer.schemas.actions import Action, ActionContext, ActionTarget
from trapspringer.schemas.validation import ValidationRequest


def test_validation_blocks_attack_on_concealed_area4_draconian_until_revealed():
    orch = Orchestrator()
    orch.start_campaign("TEST-WAVE5", user_character_id="PC_TANIS")
    orch.layer9.instantiate_scene_graph("AREA4", "AREA4_AMBUSH_MAP")
    action = Action("ACT-HIDDEN", "PC_TANIS", "melee_attack", ActionContext(mode="combat", phase="declaration", scene_id="AREA4"), target=ActionTarget("actor", "AREA4_BAAZ_1"))
    # Add a minimal target into state so failure comes from visibility, not absence.
    state = orch.layer3.read_state()
    state["characters"]["AREA4_BAAZ_1"] = state["characters"]["HOBGOBLIN_EVENT1_1"]
    state["characters"]["AREA4_BAAZ_1"].actor_id = "AREA4_BAAZ_1"
    result = orch.layer5.validate_action(ValidationRequest("VAL-HIDDEN", action, {"mode": "combat", "phase": "declaration", "state": state, "map_service": orch.layer9}))
    assert result.status == "impossible"
    assert "see" in (result.human_reason or "").lower()

    orch.layer9.reveal_entity("AREA4", "AREA4_BAAZ_1")
    result2 = orch.layer5.validate_action(ValidationRequest("VAL-SHOWN", action, {"mode": "combat", "phase": "declaration", "state": state, "map_service": orch.layer9}))
    assert result2.status == "valid"
