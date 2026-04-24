from trapspringer.engine.orchestrator import Orchestrator


def test_toede_scripted_flee():
    orch = Orchestrator()
    session = orch.start_campaign("TEST-TOEDE", user_character_id="PC_TANIS")
    orch.step(session)
    orch.step(session, "I wait")
    state = orch.layer3.read_state()
    assert state["characters"]["NPC_TOEDE"].status == "fled"
    assert state["module"].world_flags["toede_fled"] is True
