from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, is_dataclass
from typing import Any


def to_plain(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {str(k): to_plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_plain(v) for v in value]
    return value


class EventLog:
    """Append-only audit event log.

    The log normalizes events into plain dicts, assigns a monotonically
    increasing sequence number, and preserves insertion order for replay.
    """

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self.sequence = 0

    def append(self, event: dict[str, Any]) -> str:
        self.sequence += 1
        normalized = deepcopy(to_plain(event))
        normalized.setdefault("event_id", f"EVT-{self.sequence:06d}")
        normalized["sequence"] = self.sequence
        normalized.setdefault("event_type", "generic_event")
        normalized.setdefault("source_layer", "unknown")
        normalized.setdefault("visibility", "dm_private")
        normalized.setdefault("payload", {})
        self.events.append(normalized)
        return str(normalized["event_id"])

    def events_after(self, sequence: int, to_sequence: int | None = None) -> list[dict[str, Any]]:
        upper = to_sequence if to_sequence is not None else self.sequence
        return [deepcopy(e) for e in self.events if sequence < int(e.get("sequence", 0)) <= upper]

    def public_events(self) -> list[dict[str, Any]]:
        return [deepcopy(e) for e in self.events if e.get("visibility") == "public_table"]
