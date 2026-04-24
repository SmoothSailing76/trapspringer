from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class PublicSession:
    session_id: str
    campaign_id: str
    module_id: str
    active_scene_id: str | None = None
    current_milestone: str | None = None

@dataclass(slots=True)
class PublicTurnResult:
    narration: str | None = None
    prompt: str | None = None
    public_events: list[dict[str, Any]] = field(default_factory=list)
    status: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class PublicStateView:
    campaign_id: str
    active_scene_id: str | None
    milestone_id: str | None
    milestone_label: str | None
    party: list[dict[str, Any]] = field(default_factory=list)
    public_flags: dict[str, Any] = field(default_factory=dict)
