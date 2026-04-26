from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class PathRecord:
    """A stored plotted path required before movement.

    Implements the Hourglass movement handoff: destination declaration must
    become a plotted path before movement resolution.
    """

    path_id: str
    path_name: str
    start_square: str
    waypoints: list[str]
    rules: dict[str, Any] = field(default_factory=dict)
    created_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    goal_square: str | None = None
    target_area: str | None = None
    scene_id: str | None = None
    actor_id: str | None = None
    status: str = "plotted"

    def as_dict(self) -> dict[str, Any]:
        return {
            "path_id": self.path_id,
            "path_name": self.path_name,
            "start_square": self.start_square,
            "goal_square": self.goal_square,
            "target_area": self.target_area,
            "waypoints": list(self.waypoints),
            "rules": dict(self.rules),
            "created_utc": self.created_utc,
            "scene_id": self.scene_id,
            "actor_id": self.actor_id,
            "status": self.status,
        }


@dataclass(slots=True)
class PathPlotRequest:
    actor_id: str
    scene_id: str
    destination_square: str | None = None
    destination_area: str | None = None
    allow_diagonal: bool = False
    rules: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PathPlotResult:
    ok: bool
    path: PathRecord | None = None
    reason: str | None = None
    alternatives: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "path": self.path.as_dict() if self.path else None,
            "reason": self.reason,
            "alternatives": list(self.alternatives),
        }
