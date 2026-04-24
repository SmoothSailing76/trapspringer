from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ScenarioScript, ScenarioStep


def _step_from_raw(raw: dict[str, Any]) -> ScenarioStep:
    op = raw.get("op") or raw.get("action")
    if not op:
        raise ValueError(f"Scenario step is missing 'op': {raw}")
    args = dict(raw)
    args.pop("op", None)
    args.pop("action", None)
    when = args.pop("when", None)
    return ScenarioStep(op=op, args=args, when=when)


def load_scenario_script(path: str | Path) -> ScenarioScript:
    raw = json.loads(Path(path).read_text())
    return ScenarioScript(
        script_id=raw["id"],
        scene_id=raw.get("scene_id"),
        description=raw.get("description"),
        on_enter=[_step_from_raw(step) for step in raw.get("on_enter", [])],
        metadata=raw.get("metadata", {}),
    )
