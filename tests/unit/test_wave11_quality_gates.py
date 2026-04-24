from trapspringer.adapters.cli.session_runner import run_event1_demo
from trapspringer.layers.layer10_audit.leak_detection import scan_public_narration_for_leaks
from trapspringer.services.quality_service import QualityGateService


def test_public_leak_detector_flags_debug_terms():
    events = [
        {"event_id": "EVT-X", "sequence": 1, "event_type": "narration_event", "visibility": "public_table", "payload": {"spoken_text": "The dm_private secret door is obvious."}}
    ]
    issues = scan_public_narration_for_leaks(events)
    assert issues
    assert issues[0]["term"] in {"dm_private", "secret door"}


def test_quality_gates_run_on_event1_demo():
    demo = run_event1_demo(user_input="I attack the nearest hobgoblin")
    report = QualityGateService().run(demo.orchestrator)
    assert report.status in {"ok", "warning"}
    names = {check.name for check in report.checks}
    assert "public_leak_scan" in names
    assert "character_state_consistency" in names
    assert "snapshot_presence" in names
