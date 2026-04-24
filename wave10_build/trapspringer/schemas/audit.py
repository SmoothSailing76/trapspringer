from dataclasses import dataclass, field

@dataclass(slots=True)
class AuditEvent:
    event_id: str
    sequence: int
    event_type: str
    source_layer: str
    visibility: str
    payload: dict[str, object] = field(default_factory=dict)

@dataclass(slots=True)
class Snapshot:
    snapshot_id: str
    event_sequence: int
    label: str | None = None
    state_hash: str | None = None
    payload: dict[str, object] = field(default_factory=dict)

@dataclass(slots=True)
class IntegrityReport:
    check_id: str
    status: str
    issues: list[dict[str, object]] = field(default_factory=list)

@dataclass(slots=True)
class ReplayRequest:
    replay_id: str
    from_snapshot: str
    to_event_sequence: int
    mode: str

@dataclass(slots=True)
class ReplayResult:
    replay_id: str
    status: str
    payload: dict[str, object] = field(default_factory=dict)
