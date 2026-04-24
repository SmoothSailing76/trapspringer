from __future__ import annotations

from copy import deepcopy
from typing import Any

from trapspringer.services.hash_service import stable_hash


def _get_child(container: Any, key: str) -> Any:
    if isinstance(container, dict):
        return container[key]
    return getattr(container, key)


def _set_child(container: Any, key: str, value: Any) -> Any:
    if isinstance(container, dict):
        container[key] = value
    else:
        setattr(container, key, value)


def _apply_diff(state: dict[str, Any], diff: dict[str, Any]) -> None:
    path = str(diff.get("path", ""))
    if not path:
        return
    cursor: Any = state
    parts = path.split(".")
    for part in parts[:-1]:
        cursor = _get_child(cursor, part)
    _set_child(cursor, parts[-1], deepcopy(diff.get("new")))


def _apply_event(state: dict[str, Any], event: dict[str, Any]) -> None:
    event_type = event.get("event_type")
    payload = event.get("payload", {}) or {}
    if event_type != "state_mutation_event":
        return
    commit = payload.get("commit", {}) or {}
    for diff in commit.get("diffs", []) or []:
        _apply_diff(state, diff)


def replay_from_snapshot(snapshot: dict[str, Any] | None, events: list[dict[str, Any]], to_event_sequence: int | None = None) -> dict[str, Any]:
    if snapshot is None:
        return {"status": "error", "error": "snapshot_not_found", "events_applied": 0}
    start_sequence = int(snapshot.get("event_sequence", 0))
    target = to_event_sequence if to_event_sequence is not None else (int(events[-1].get("sequence", 0)) if events else start_sequence)
    state = deepcopy(snapshot.get("payload", {}))
    applied: list[str] = []
    for event in events:
        seq = int(event.get("sequence", 0))
        if start_sequence < seq <= target:
            _apply_event(state, event)
            applied.append(str(event.get("event_id", seq)))
    return {
        "status": "ok",
        "from_snapshot": snapshot.get("snapshot_id"),
        "from_sequence": start_sequence,
        "to_sequence": target,
        "events_applied": len(applied),
        "applied_event_ids": applied,
        "state": state,
        "state_hash": stable_hash(state),
    }
