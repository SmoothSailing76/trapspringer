from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class ResourceChange:
    owner: str
    resource_type: str
    delta: int
    note: str | None = None

@dataclass(slots=True)
class FollowupCheck:
    check_type: str
    target: str
    trigger: str

@dataclass(slots=True)
class PrivateOutcome:
    summary: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class PublicOutcome:
    narration: str | None = None
    public_state_changes: list[str] = field(default_factory=list)

@dataclass(slots=True)
class ResolutionRequest:
    resolution_id: str
    action_id: str
    actor_id: str
    scene_id: str
    mode: str
    payload: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class ResolutionResult:
    resolution_id: str
    status: str
    private_outcome: PrivateOutcome = field(default_factory=PrivateOutcome)
    public_outcome: PublicOutcome = field(default_factory=PublicOutcome)
    state_mutations: list[dict[str, Any]] = field(default_factory=list)
    knowledge_effects: list[dict[str, Any]] = field(default_factory=list)
    followup_checks: list[FollowupCheck] = field(default_factory=list)
    resource_changes: list[ResourceChange] = field(default_factory=list)
