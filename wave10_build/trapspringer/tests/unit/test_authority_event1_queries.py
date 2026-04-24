from trapspringer.engine.orchestrator import Orchestrator


def test_authority_event1_queries():
    orch = Orchestrator()
    session = orch.start_campaign("TEST-AUTH", user_character_id="PC_TANIS")
    state = orch.layer3.read_state()
    attacker = state["characters"]["PC_TANIS"]
    target = state["characters"]["HOBGOBLIN_EVENT1_1"]
    needed = orch.layer1.attack_target_number(attacker, target)
    assert isinstance(needed, int)
    assert needed >= 2
    assert "flees" in (orch.layer1.event1_script("toede_opening") or "").lower()
