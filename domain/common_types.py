from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class TimeRef:
    day: int = 1
    hour: int = 0
    turn: int = 0
    round: int = 0
    segment: int = 0

@dataclass(slots=True)
class AuthorityTraceRef:
    selected_source: str | None = None
    domain: str | None = None
    precedence_reason: str | None = None

@dataclass(slots=True)
class PositionRef:
    area_id: str
    sub_area_id: str | None = None
    zone: str | None = None
    x: int | None = None
    y: int | None = None
    z: int | None = None

@dataclass(slots=True)
class RecipientScope:
    recipient: str
    actor_ids: list[str] = field(default_factory=list)

@dataclass(slots=True)
class MutationRef:
    path: str
    old: Any
    new: Any

@dataclass(slots=True)
class FactRef:
    fact_id: str
