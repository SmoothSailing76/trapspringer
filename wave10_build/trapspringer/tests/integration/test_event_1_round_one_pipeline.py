from trapspringer.engine.orchestrator import Orchestrator


def test_event_1_round_one_pipeline():
    orch = Orchestrator()
    session = orch.start_campaign("TEST-CAMPAIGN", user_character_id="PC_TANIS")
    orch.step(session)
    result = orch.step(session, "I attack the nearest hobgoblin")
    state = orch.layer3.read_state()

    assert "Fewmaster Toede" in result.narration
    assert state["characters"]["NPC_TOEDE"].status == "fled"
    assert state["module"].world_flags["toede_fled"] is True
    assert state["time"].round == 1
    assert result.validations
    assert result.resolutions
    assert len(orch.layer10.event_log.events) > 10
    assert any(c.current_hp < c.max_hp or c.status == "defeated" for c in state["characters"].values())
