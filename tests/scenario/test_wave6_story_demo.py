from trapspringer.engine.orchestrator import Orchestrator


def test_wave6_story_demo_adds_goldmoon_and_riverwind():
    orchestrator = Orchestrator()
    session = orchestrator.start_campaign("TEST-WAVE6", user_character_id="PC_TANIS")
    orchestrator.step(session)
    orchestrator.step(session, "I attack the nearest hobgoblin")
    outputs = orchestrator.run_wave6_story_demo(session)

    state = orchestrator.layer3.read_state()
    assert "PC_GOLDMOON" in state["party"].member_ids
    assert "NPC_RIVERWIND" in state["party"].member_ids
    assert state["module"].world_flags["goldmoon_joined"] is True
    assert state["module"].quest_flags["staff_in_party_possession"] is True
    assert any("blue crystal staff" in (o.narration or "").lower() for o in outputs)


def test_wave6_wicker_dragon_and_khisanth_flags():
    orchestrator = Orchestrator()
    session = orchestrator.start_campaign("TEST-WAVE6B", user_character_id="PC_TANIS")
    orchestrator.step(session)
    orchestrator.step(session, "I attack the nearest hobgoblin")
    orchestrator.trigger_event2_goldmoon()
    orchestrator.transition_to_scene("DL1_AREA_44F")
    wicker = orchestrator.inspect_wicker_dragon("PC_TASSLEHOFF")
    orchestrator.transition_to_scene("DL1_AREA_44K")
    khisanth = orchestrator.trigger_khisanth_surface()

    state = orchestrator.layer3.read_state()
    assert state["module"].world_flags["wicker_dragon_discovered"] is True
    assert "wicker" in (wicker.narration or "").lower()
    assert state["module"].world_flags["khisanth_surface_seen"] is True
    assert "khisanth" in (khisanth.narration or "").lower()
