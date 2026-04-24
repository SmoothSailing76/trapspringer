from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def switch_mode(frame, new_mode: str, reason: str | None = None):
    frame.mode = new_mode
    frame.phase = "prompt"
    return frame


@dataclass(slots=True)
class MainPathMilestone:
    id: str
    scene_id: str
    label: str
    required_flags: list[str]
    sets_flags: list[str]
    checkpoint: bool
    next: list[str]


def load_main_path_registry(path: str | Path | None = None) -> dict[str, MainPathMilestone]:
    registry_path = Path(path) if path is not None else PACKAGE_ROOT / "data/dl1/main_path_registry.json"
    raw = json.loads(registry_path.read_text())
    out: dict[str, MainPathMilestone] = {}
    for item in raw.get("milestones", []):
        ms = MainPathMilestone(
            id=str(item["id"]),
            scene_id=str(item["scene_id"]),
            label=str(item["label"]),
            required_flags=list(item.get("required_flags", [])),
            sets_flags=list(item.get("sets_flags", [])),
            checkpoint=bool(item.get("checkpoint", False)),
            next=list(item.get("next", [])),
        )
        out[ms.id] = ms
    return out


def milestone_order(path: str | Path | None = None) -> list[str]:
    registry_path = Path(path) if path is not None else PACKAGE_ROOT / "data/dl1/main_path_registry.json"
    raw = json.loads(registry_path.read_text())
    return [str(item["id"]) for item in raw.get("milestones", [])]


def _flag_is_set(module_state: Any, flag: str) -> bool:
    return bool(getattr(module_state, "world_flags", {}).get(flag) or getattr(module_state, "quest_flags", {}).get(flag))


def validate_main_path_transition(current_id: str | None, next_id: str, registry: dict[str, MainPathMilestone] | None, module_state: Any) -> tuple[bool, str | None]:
    registry = registry or load_main_path_registry()
    if next_id not in registry:
        return False, f"Unknown main-path milestone: {next_id}."
    if current_id is None:
        current_id = str(getattr(module_state, "world_flags", {}).get("current_milestone") or "start_of_event_1")
    if current_id not in registry:
        return False, f"Unknown current milestone: {current_id}."
    # Re-applying the current milestone is allowed for idempotent status/checkpoint repair.
    if next_id != current_id and next_id not in registry[current_id].next:
        return False, f"Cannot transition from {current_id} to {next_id}; allowed: {registry[current_id].next}."
    missing = [flag for flag in registry[next_id].required_flags if not _flag_is_set(module_state, flag)]
    if missing:
        return False, f"Cannot transition to {next_id}; missing required flag(s): {', '.join(missing)}."
    return True, None


def apply_milestone_flags(milestone_id: str, registry: dict[str, MainPathMilestone] | None, module_state: Any) -> list[str]:
    from trapspringer.layers.layer3_state.module_flags import set_module_flags
    registry = registry or load_main_path_registry()
    milestone = registry[milestone_id]
    set_module_flags(module_state, milestone.sets_flags)
    module_state.world_flags["current_milestone"] = milestone_id
    if milestone_id not in module_state.resolved_encounters:
        module_state.resolved_encounters.append(milestone_id)
    return list(milestone.sets_flags)
