from trapspringer.engine.orchestrator import Orchestrator


def test_event_1_round_replay_matches_after_round_snapshot():
    orch = Orchestrator()
    session = orch.start_campaign(user_character_id="PC_TANIS")
    start_snapshot = session.context.current_snapshot_id
    orch.step(session)
    orch.step(session, "I attack nearest hobgoblin")
    latest = orch.layer10.snapshots.latest()
    replay = orch.layer10.replay({
        "from_snapshot": start_snapshot,
        "to_event_sequence": latest["event_sequence"],
    })
    assert replay["status"] == "ok"
    assert replay["state_hash"] == latest["state_hash"]


def test_recap_is_generated_from_audit_events():
    orch = Orchestrator()
    session = orch.start_campaign(user_character_id="PC_TANIS")
    orch.step(session)
    orch.step(session, "I attack nearest hobgoblin")
    recap = orch.layer10.recap(limit=12)
    assert "Roll" in recap or "Toede" in recap
