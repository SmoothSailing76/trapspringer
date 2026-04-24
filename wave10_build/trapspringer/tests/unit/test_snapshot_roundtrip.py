from trapspringer.engine.orchestrator import Orchestrator


def test_snapshot_roundtrip():
    orch = Orchestrator()
    session = orch.start_campaign("TEST-SNAPSHOT", user_character_id="PC_TANIS")
    snapshot_id = session.context.current_snapshot_id
    snapshot = orch.layer10.get_snapshot(snapshot_id)
    assert snapshot is not None
    assert snapshot["label"] == "start_of_event_1"
    assert snapshot["state_hash"]
