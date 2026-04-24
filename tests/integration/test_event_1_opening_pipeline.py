from trapspringer.engine.orchestrator import Orchestrator


def test_event_1_opening_pipeline():
    orchestrator = Orchestrator()
    session = orchestrator.start_campaign("TEST-CAMPAIGN", user_character_id="PC_TANIS")
    state = orchestrator.layer3.read_state()

    assert session.context.module_id == "DL1_DRAGONS_OF_DESPAIR"
    assert session.context.active_scene_id == "DL1_EVENT_1_AMBUSH"
    assert state["module"].triggered_events["EVENT_1"] is True
    assert "PC_TANIS" in state["party"].member_ids
    assert "DL1_EVENT_1_AMBUSH" in orchestrator.layer9.scene_graphs

    graph = orchestrator.layer9.scene_graphs["DL1_EVENT_1_AMBUSH"]
    assert graph.zone_of("NPC_TOEDE") == "toede_front"
    assert graph.zone_of("HOBGOBLIN_EVENT1_1") in {"left_woodline", "right_woodline"}

    result = orchestrator.step(session)
    assert "Hobgoblins emerge" in result.narration
    assert "Declare your first actions" in result.prompt
    assert session.context.current_snapshot_id is not None
