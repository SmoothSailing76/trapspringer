from trapspringer.engine.orchestrator import Orchestrator


def test_event_1_completion_check_round_one():
    orch = Orchestrator()
    session = orch.start_campaign("TEST-COMPLETE", user_character_id="PC_TANIS")
    opening = orch.step(session)
    assert "Hobgoblins" in opening.narration
    result = orch.step(session, "I attack the nearest hobgoblin")
    state = orch.layer3.read_state()
    assert state["scene"].scene_id == "DL1_EVENT_1_AMBUSH"
    assert state["module"].triggered_events["EVENT_1"] is True
    assert state["characters"]["NPC_TOEDE"].status == "fled"
    assert state["time"].round == 1
    assert result.validations
    assert result.resolutions
    assert result.narration
    assert orch.layer10.get_snapshot(session.context.current_snapshot_id) is not None
    assert orch.layer10.check_integrity()["status"] in {"ok", "warning"}
