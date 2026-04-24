from trapspringer.engine.orchestrator import Orchestrator


def test_snapshot_and_integrity_after_startup():
    orch = Orchestrator()
    session = orch.start_campaign(user_character_id="PC_TANIS")
    assert session.context.current_snapshot_id == "SNAP-000001"
    assert orch.layer10.get_snapshot("SNAP-000001") is not None
    report = orch.layer10.check_integrity()
    assert report["status"] == "ok"


def test_round_logging_includes_rolls_and_mutations():
    orch = Orchestrator()
    session = orch.start_campaign(user_character_id="PC_TANIS")
    orch.step(session)
    orch.step(session, "I attack nearest hobgoblin")
    event_types = [e["event_type"] for e in orch.layer10.event_log.events]
    assert "roll_event" in event_types
    assert "state_mutation_event" in event_types
    assert "snapshot_event" in event_types
