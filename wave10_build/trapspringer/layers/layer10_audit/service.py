from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from trapspringer.layers.layer10_audit.event_log import EventLog, to_plain
from trapspringer.layers.layer10_audit.integrity import check_integrity
from trapspringer.layers.layer10_audit.recaps import recap_round
from trapspringer.layers.layer10_audit.replay import replay_from_snapshot
from trapspringer.layers.layer10_audit.snapshots import SnapshotStore, build_snapshot


def _to_plain(obj: Any) -> Any:
    return to_plain(obj)


class AuditReplayService:
    def __init__(self) -> None:
        self.event_log = EventLog()
        self.snapshots = SnapshotStore()

    def append_event(self, event: Any) -> str:
        if is_dataclass(event):
            event = asdict(event)
        elif hasattr(event, "__dict__"):
            event = dict(event.__dict__)
        return self.event_log.append(event)

    def append_event_from_dict(self, event: dict[str, Any]) -> str:
        return self.event_log.append(event)

    def create_snapshot(self, label: str | None = None, state: dict | None = None, milestone_id: str | None = None) -> str:
        snapshot_id = f"SNAP-{len(self.snapshots.snapshots)+1:06d}"
        snapshot = build_snapshot(snapshot_id, _to_plain(state or {}), event_sequence=self.event_log.sequence, label=label, milestone_id=milestone_id or label)
        self.snapshots.put(snapshot_id, snapshot)
        self.append_event_from_dict({
            "event_id": f"EVT-SNAPSHOT-{snapshot_id}",
            "event_type": "snapshot_event",
            "source_layer": "layer10",
            "visibility": "dm_private",
            "payload": {
                "snapshot_id": snapshot_id,
                "label": label,
                "milestone_id": milestone_id or label,
                "state_hash": snapshot["state_hash"],
                "save_schema_version": snapshot["save_schema_version"],
                "engine_version": snapshot["engine_version"],
            },
        })
        return snapshot_id

    def create_named_checkpoint(self, milestone_id: str, state: dict | None = None, label: str | None = None) -> str:
        return self.create_snapshot(label or milestone_id, state=state, milestone_id=milestone_id)

    def checkpoint_ids(self) -> dict[str, str]:
        return dict(getattr(self.snapshots, "named", {}))

    def get_snapshot(self, snapshot_id: str) -> dict[str, Any] | None:
        return self.snapshots.get(snapshot_id)

    def replay(self, request: dict | None = None) -> dict[str, Any]:
        request = request or {}
        snapshot_id = str(request.get("from_snapshot") or request.get("snapshot_id") or "")
        snapshot = self.snapshots.get(snapshot_id)
        return replay_from_snapshot(snapshot, self.event_log.events, request.get("to_event_sequence"))

    def check_integrity(self, range=None) -> dict[str, Any]:
        return check_integrity(self.event_log.events)

    def recap(self, limit: int | None = None) -> str:
        return recap_round(self.event_log.events, limit=limit)
