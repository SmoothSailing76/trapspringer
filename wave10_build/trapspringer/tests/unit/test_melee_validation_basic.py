from trapspringer.engine.orchestrator import Orchestrator
from trapspringer.layers.layer5_validation.parser import parse_user_declaration
from trapspringer.schemas.validation import ValidationRequest


def test_melee_validation_basic():
    orch = Orchestrator()
    orch.start_campaign("TEST-CAMPAIGN", user_character_id="PC_TANIS")
    state = orch.layer3.read_state()
    decl = parse_user_declaration("I attack the nearest hobgoblin", "PC_TANIS", "ACT-TEST")
    result = orch.layer5.validate_action(ValidationRequest("VAL-TEST", decl.action, {"mode": "combat", "state": state, "map_service": orch.layer9}))
    assert result.status == "valid"
