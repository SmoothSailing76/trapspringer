from trapspringer.engine.orchestrator import Orchestrator
from trapspringer.layers.layer5_validation.parser import parse_user_declaration
from trapspringer.schemas.resolution import ResolutionRequest


def test_melee_resolution_basic():
    orch = Orchestrator()
    orch.start_campaign("TEST-CAMPAIGN", user_character_id="PC_TANIS")
    state = orch.layer3.read_state()
    decl = parse_user_declaration("I attack nearest hobgoblin", "PC_TANIS", "ACT-TEST")
    decl.action.extra["resolved_target_id"] = "HOBGOBLIN_EVENT1_1"
    result = orch.layer6.resolve(ResolutionRequest("RES-TEST", decl.action.action_id, decl.actor_id, "DL1_EVENT_1_AMBUSH", "combat", {"action": decl.action, "state": state, "map_service": orch.layer9}))
    assert result.status == "resolved"
    assert result.private_outcome.summary["target_id"] == "HOBGOBLIN_EVENT1_1"
