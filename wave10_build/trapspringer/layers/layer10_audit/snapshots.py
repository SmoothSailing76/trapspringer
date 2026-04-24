from __future__ import annotations

from copy import deepcopy
from typing import Any

from trapspringer.layers.layer10_audit.event_log import to_plain
from trapspringer.services.hash_service import stable_hash

SAVE_SCHEMA_VERSION = "0.2"
ENGINE_VERSION = "0.2.0"


class SnapshotStore:
    def __init__(self) -> None:
        self.snapshots: dict[str, dict[str, Any]] = {}
        self.named: dict[str, str] = {}

    def put(self, snapshot_id: str, payload: dict[str, Any]) -> None:
        snap = deepcopy(payload)
        self.snapshots[snapshot_id] = snap
        label = snap.get("label") or snap.get("milestone_id")
        if label:
            self.named[str(label)] = snapshot_id
        milestone = snap.get("milestone_id") or (snap.get("metadata") or {}).get("milestone_id")
        if milestone:
            self.named[str(milestone)] = snapshot_id

    def get(self, snapshot_id: str) -> dict[str, Any] | None:
        key = self.named.get(snapshot_id, snapshot_id)
        snap = self.snapshots.get(key)
        return deepcopy(snap) if snap is not None else None

    def latest(self) -> dict[str, Any] | None:
        if not self.snapshots:
            return None
        key = sorted(self.snapshots.keys())[-1]
        return self.get(key)

    def by_label(self, label: str) -> dict[str, Any] | None:
        return self.get(label)


def build_snapshot(snapshot_id: str, state: dict[str, Any], event_sequence: int = 0, label: str | None = None, milestone_id: str | None = None) -> dict[str, Any]:
    payload = to_plain(state or {})
    metadata = {
        "label": label,
        "milestone_id": milestone_id or label,
        "save_schema_version": SAVE_SCHEMA_VERSION,
        "engine_version": ENGINE_VERSION,
    }
    return {
        "snapshot_id": snapshot_id,
        "label": label,
        "milestone_id": milestone_id or label,
        "event_sequence": int(event_sequence),
        "state_hash": stable_hash(payload),
        "payload": payload,
        "save_schema_version": SAVE_SCHEMA_VERSION,
        "engine_version": ENGINE_VERSION,
        "metadata": metadata,
    }


def create_named_checkpoint(snapshot_store: SnapshotStore, state: dict[str, Any], label: str, milestone_id: str, event_sequence: int = 0) -> dict[str, Any]:
    snapshot_id = f"SNAP-{len(snapshot_store.snapshots)+1:06d}"
    snap = build_snapshot(snapshot_id, state, event_sequence=event_sequence, label=label, milestone_id=milestone_id)
    snapshot_store.put(snapshot_id, snap)
    return snap
