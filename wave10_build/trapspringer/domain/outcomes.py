from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class ValidationOutcome:
    status: str
    human_reason: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class ResolutionOutcome:
    status: str
    private_outcome: dict[str, Any] = field(default_factory=dict)
    public_outcome: dict[str, Any] = field(default_factory=dict)
    state_mutations: list[dict[str, Any]] = field(default_factory=list)

@dataclass(slots=True)
class NarrationBundle:
    spoken_text: str
    prompt: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class PartyDiscussionBundle:
    discussion: list[dict[str, Any]] = field(default_factory=list)
    caller_summary: str | None = None
    declarations: list[dict[str, Any]] = field(default_factory=list)

@dataclass(slots=True)
class SpatialQueryResult:
    status: str
    payload: dict[str, Any] = field(default_factory=dict)
