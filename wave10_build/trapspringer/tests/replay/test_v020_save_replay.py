from trapspringer.engine.orchestrator import Orchestrator


def test_v020_replay_from_first_snapshot_has_hash():
    orch = Orchestrator()
    session = orch.start_campaign("TEST-V020-REPLAY")
    orch.step(session)
    orch.step(session, "I attack the nearest hobgoblin")
    orch.run_v020_main_path_demo(session)
    first = next(iter(orch.layer10.snapshots.snapshots.keys()))
    result = orch.layer10.replay({"from_snapshot": first})
    assert result["status"] == "ok"
    assert result["from_snapshot"] == first
    assert "state_hash" in result
