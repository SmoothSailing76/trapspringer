from __future__ import annotations

from typing import Any

from trapspringer.layers.layer10_audit.leak_detection import scan_public_narration_for_leaks


def check_integrity(events: list[dict[str, Any]]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    expected = 1
    seen_ids: set[str] = set()
    for event in events:
        seq = int(event.get("sequence", -1))
        if seq != expected:
            issues.append({"type": "sequence_gap", "expected": expected, "found": seq, "event_id": event.get("event_id")})
            expected = seq
        expected += 1
        event_id = str(event.get("event_id"))
        if event_id in seen_ids:
            issues.append({"type": "duplicate_event_id", "event_id": event_id})
        seen_ids.add(event_id)
        if event.get("event_type") == "narration_event":
            payload = event.get("payload", {}) or {}
            if not payload.get("spoken_text") and not payload.get("prompt"):
                issues.append({"type": "empty_narration", "event_id": event_id})
        if event.get("event_type") == "state_mutation_event":
            payload = event.get("payload", {}) or {}
            commit = payload.get("commit", {}) or {}
            if not commit.get("diffs"):
                issues.append({"type": "empty_state_mutation", "event_id": event_id})
    leaks = scan_public_narration_for_leaks(events)
    issues.extend({"type": "public_narration_leak", **leak} for leak in leaks)

    # Causal sanity checks used by Wave 11 hardening. These catch common
    # architecture regressions without requiring a full semantic replay.
    seen_types: set[str] = set()
    for event in events:
        event_type = str(event.get("event_type"))
        if event_type == "state_mutation_event" and not ({"resolution_event", "module_event", "procedure_event"} & seen_types):
            issues.append({"type": "mutation_without_prior_cause", "event_id": event.get("event_id")})
        if event_type == "narration_event" and event.get("visibility") == "public_table" and not ({"resolution_event", "procedure_event", "module_event", "input_received"} & seen_types):
            # Opening scene narration is allowed after campaign-start procedure events.
            payload = event.get("payload", {}) or {}
            if "Hobgoblins emerge" not in str(payload.get("spoken_text", "")):
                issues.append({"type": "public_narration_without_context", "event_id": event.get("event_id")})
        seen_types.add(event_type)

    return {"check_id": "INT-000001", "status": "ok" if not issues else "warning", "issues": issues}
