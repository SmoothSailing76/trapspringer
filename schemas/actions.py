from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class ActionTarget:
    kind: str
    id: str

@dataclass(slots=True)
class MovementComponent:
    declared: bool = False
    destination: str | None = None

@dataclass(slots=True)
class ActionContext:
    mode: str
    phase: str | None = None
    scene_id: str | None = None

@dataclass(slots=True)
class Action:
    action_id: str
    actor_id: str
    action_type: str
    context: ActionContext
    target: ActionTarget | None = None
    method: str | None = None
    tools_used: list[str] = field(default_factory=list)
    movement_component: MovementComponent | None = None
    spoken_text: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)
