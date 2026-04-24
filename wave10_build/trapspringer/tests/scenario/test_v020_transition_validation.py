from trapspringer.engine.orchestrator import Orchestrator
from trapspringer.layers.layer4_procedure.transitions import load_main_path_registry, validate_main_path_transition


def test_invalid_jump_to_lair_is_blocked():
    orch = Orchestrator()
    orch.start_campaign("TEST-TRANSITION")
    state = orch.layer3.read_state()
    registry = load_main_path_registry()
    ok, reason = validate_main_path_transition("start_of_event_1", "before_70k", registry, state["module"])
    assert not ok
    assert "Cannot transition" in reason or "missing" in reason


def test_valid_first_transition_passes():
    orch = Orchestrator()
    orch.start_campaign("TEST-TRANSITION")
    state = orch.layer3.read_state()
    registry = load_main_path_registry()
    ok, reason = validate_main_path_transition("start_of_event_1", "after_event_1", registry, state["module"])
    assert ok, reason
