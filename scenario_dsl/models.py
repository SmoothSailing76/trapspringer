from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True, slots=True)
class ScenarioStep:
    op: str
    args: dict[str, Any] = field(default_factory=dict)
    when: dict[str, Any] | None = None

@dataclass(frozen=True, slots=True)
class ScenarioScript:
    script_id: str
    scene_id: str | None = None
    description: str | None = None
    on_enter: list[ScenarioStep] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class ScenarioResult:
    script_id: str
    executed_steps: list[str] = field(default_factory=list)
    skipped_steps: list[str] = field(default_factory=list)
    mutations: list[dict[str, Any]] = field(default_factory=list)
    narration: list[str] = field(default_factory=list)
    checkpoints: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors
