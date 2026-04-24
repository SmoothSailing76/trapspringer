from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SUPPORTED_HOOKS = (
    "on_enter",
    "on_exit",
    "on_prompt",
    "on_declaration",
    "on_validation_failure",
    "on_resolution",
    "on_round_start",
    "on_round_end",
    "on_milestone",
)

SUPPORTED_OPS = {
    "set_flag",
    "clear_flag",
    "reveal",
    "reveal_fact",
    "narrate",
    "emit_narration_block",
    "checkpoint",
    "create_checkpoint",
    "transition",
    "trigger_scene",
    "add_item",
    "remove_item",
    "move_actor",
    "damage_actor",
    "heal_actor",
    "start_escape_mode",
    "run_named_script",
}

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
    on_exit: list[ScenarioStep] = field(default_factory=list)
    on_prompt: list[ScenarioStep] = field(default_factory=list)
    on_declaration: list[ScenarioStep] = field(default_factory=list)
    on_validation_failure: list[ScenarioStep] = field(default_factory=list)
    on_resolution: list[ScenarioStep] = field(default_factory=list)
    on_round_start: list[ScenarioStep] = field(default_factory=list)
    on_round_end: list[ScenarioStep] = field(default_factory=list)
    on_milestone: list[ScenarioStep] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def steps_for_hook(self, hook: str) -> list[ScenarioStep]:
        if hook not in SUPPORTED_HOOKS:
            raise ValueError(f"Unsupported scenario hook: {hook}")
        return list(getattr(self, hook))

@dataclass(slots=True)
class ScenarioResult:
    script_id: str
    hook: str = "on_enter"
    executed_steps: list[str] = field(default_factory=list)
    skipped_steps: list[str] = field(default_factory=list)
    mutations: list[dict[str, Any]] = field(default_factory=list)
    knowledge_effects: list[dict[str, Any]] = field(default_factory=list)
    map_effects: list[dict[str, Any]] = field(default_factory=list)
    narration: list[str] = field(default_factory=list)
    checkpoints: list[str] = field(default_factory=list)
    transitions: list[str] = field(default_factory=list)
    inventory_effects: list[dict[str, Any]] = field(default_factory=list)
    audit_events: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors
