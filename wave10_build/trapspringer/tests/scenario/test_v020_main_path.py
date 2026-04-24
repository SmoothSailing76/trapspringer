from trapspringer.engine.orchestrator import Orchestrator


def test_v020_main_path_reaches_epilogue():
    orch = Orchestrator()
    session = orch.start_campaign("TEST-V020")
    orch.step(session)
    orch.step(session, "I attack the nearest hobgoblin")
    outputs = orch.run_v020_main_path_demo(session)
    state = orch.layer3.read_state()
    assert outputs[-1].prompt == "The quest of DL1 is complete."
    assert state["module"].quest_flags["disks_recovered"] is True
    assert state["module"].quest_flags["khisanth_defeated"] is True
    assert state["module"].quest_flags["staff_shattered"] is True
    assert state["module"].quest_flags["medallion_created"] is True
    assert state["module"].world_flags["epilogue_complete"] is True


def test_v020_snapshots_created():
    orch = Orchestrator()
    session = orch.start_campaign("TEST-V020-SNAP")
    orch.step(session)
    orch.step(session, "I attack the nearest hobgoblin")
    orch.run_v020_main_path_demo(session)
    labels = [snap.get("label") for snap in orch.layer10.snapshots.snapshots.values()]
    assert any("dl1_temple_mishakal" in str(label) for label in labels)
    assert any("dl1_dragon_lair_70k" in str(label) for label in labels)
    assert any("dl1_collapse_epilogue" in str(label) for label in labels)
