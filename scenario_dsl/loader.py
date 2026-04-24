from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import SUPPORTED_HOOKS, ScenarioScript, ScenarioStep

def _step_from_raw(raw: dict[str, Any] | str) -> ScenarioStep:
    if isinstance(raw, str):
        return ScenarioStep(op="narrate", args={"text": raw})
    op = raw.get("op") or raw.get("action")
    if not op:
        if len(raw) == 1:
            op, value = next(iter(raw.items()))
            args = dict(value) if isinstance(value, dict) else {"value": value}
            return ScenarioStep(op=op, args=args)
        raise ValueError(f"Scenario step is missing 'op': {raw}")
    args = dict(raw)
    args.pop("op", None)
    args.pop("action", None)
    when = args.pop("when", None)
    if op == "reveal_fact":
        op = "reveal"
    if op == "create_checkpoint":
        op = "checkpoint"
    if op == "emit_narration_block":
        op = "narrate"
    return ScenarioStep(op=op, args=args, when=when)

def _steps(raw: dict[str, Any], hook: str) -> list[ScenarioStep]:
    return [_step_from_raw(step) for step in raw.get(hook, [])]

def load_scenario_script(path: str | Path) -> ScenarioScript:
    raw = json.loads(Path(path).read_text())
    data = {hook: _steps(raw, hook) for hook in SUPPORTED_HOOKS}
    return ScenarioScript(
        script_id=raw["id"],
        scene_id=raw.get("scene_id"),
        description=raw.get("description"),
        metadata=raw.get("metadata", {}),
        **data,
    )

def load_scenario_directory(path: str | Path) -> list[ScenarioScript]:
    root = Path(path)
    return [load_scenario_script(p) for p in sorted(root.glob("*.json"))]
