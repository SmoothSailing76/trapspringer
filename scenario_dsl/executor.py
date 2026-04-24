from __future__ import annotations

from typing import Any

from .models import ScenarioResult, ScenarioScript, ScenarioStep


def _get_flag(state: dict[str, Any], name: str) -> Any:
    module = state.get("module")
    if module is None:
        return None
    world = getattr(module, "world_flags", {}) or {}
    quest = getattr(module, "quest_flags", {}) or {}
    if name in world:
        return world[name]
    return quest.get(name)


def _set_flag(state: dict[str, Any], name: str, value: Any = True) -> None:
    module = state.get("module")
    if module is None:
        return
    if name in getattr(module, "quest_flags", {}):
        module.quest_flags[name] = value
    module.world_flags[name] = value


def _condition_matches(state: dict[str, Any], when: dict[str, Any] | None) -> bool:
    if not when:
        return True
    flags = when.get("flags", {})
    for flag, expected in flags.items():
        if _get_flag(state, flag) != expected:
            return False
    missing = when.get("missing_flags", [])
    for flag in missing:
        if bool(_get_flag(state, flag)):
            return False
    return True


class ScenarioScriptExecutor:
    """Executes the minimal declarative scene scripting DSL.

    Supported operations:
    - set_flag: {"flag": "staff_recharged", "value": true}
    - reveal: {"fact_id": "F-...", "scope": "party_known"}
    - narrate: {"text": "..."}
    - checkpoint: {"label": "staff_recharged"}
    - transition: {"milestone_id": "descent_started"}
    """

    def execute_on_enter(self, script: ScenarioScript, state: dict[str, Any]) -> ScenarioResult:
        result = ScenarioResult(script_id=script.script_id)
        for index, step in enumerate(script.on_enter, start=1):
            step_id = f"{step.op}:{index}"
            if not _condition_matches(state, step.when):
                result.skipped_steps.append(step_id)
                continue
            try:
                self._execute_step(step, state, result)
                result.executed_steps.append(step_id)
            except Exception as exc:  # intentionally captured for DSL authoring feedback
                result.errors.append(f"{step_id}: {exc}")
        return result

    def _execute_step(self, step: ScenarioStep, state: dict[str, Any], result: ScenarioResult) -> None:
        if step.op == "set_flag":
            flag = step.args["flag"]
            value = step.args.get("value", True)
            _set_flag(state, flag, value)
            result.mutations.append({"path": f"module.world_flags.{flag}", "value": value})
        elif step.op == "reveal":
            result.mutations.append({"knowledge": step.args})
        elif step.op == "narrate":
            result.narration.append(str(step.args.get("text", "")))
        elif step.op == "checkpoint":
            result.checkpoints.append(str(step.args["label"]))
        elif step.op == "transition":
            milestone_id = str(step.args["milestone_id"])
            _set_flag(state, "current_milestone", milestone_id)
            result.mutations.append({"path": "module.world_flags.current_milestone", "value": milestone_id})
        else:
            raise ValueError(f"Unsupported scenario DSL op: {step.op}")
