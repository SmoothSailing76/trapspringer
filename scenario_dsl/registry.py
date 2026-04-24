from __future__ import annotations

from pathlib import Path

from .loader import load_scenario_directory, load_scenario_script
from .models import ScenarioScript

class ScenarioScriptRegistry:
    def __init__(self) -> None:
        self._scripts: dict[str, ScenarioScript] = {}
        self._by_scene: dict[str, list[str]] = {}

    def register(self, script: ScenarioScript) -> ScenarioScript:
        self._scripts[script.script_id] = script
        if script.scene_id:
            self._by_scene.setdefault(script.scene_id, []).append(script.script_id)
        return script

    def load_path(self, path: str | Path) -> list[ScenarioScript]:
        p = Path(path)
        scripts = load_scenario_directory(p) if p.is_dir() else [load_scenario_script(p)]
        for script in scripts:
            self.register(script)
        return scripts

    def get(self, script_id: str) -> ScenarioScript:
        return self._scripts[script_id]

    def for_scene(self, scene_id: str) -> list[ScenarioScript]:
        return [self._scripts[sid] for sid in self._by_scene.get(scene_id, [])]

    def summary(self) -> dict:
        return {"script_count": len(self._scripts), "scenes": {k: list(v) for k, v in self._by_scene.items()}}
