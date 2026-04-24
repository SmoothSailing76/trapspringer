from __future__ import annotations

from typing import Any

from .models import ScenarioResult, ScenarioScript, ScenarioStep

def _get_module(state: dict[str, Any]) -> Any:
    return state.get("module") or state.get("module_state")

def _get_flag(state: dict[str, Any], name: str) -> Any:
    module = _get_module(state)
    if module is None:
        return state.get("flags", {}).get(name)
    world = getattr(module, "world_flags", {}) or {}
    quest = getattr(module, "quest_flags", {}) or {}
    if name in world:
        return world[name]
    if name in quest:
        return quest[name]
    return state.get("flags", {}).get(name)

def _set_flag(state: dict[str, Any], name: str, value: Any = True) -> None:
    module = _get_module(state)
    if module is None:
        state.setdefault("flags", {})[name] = value
        return
    if name in getattr(module, "quest_flags", {}):
        module.quest_flags[name] = value
    module.world_flags[name] = value

def _condition_matches(state: dict[str, Any], when: dict[str, Any] | None) -> bool:
    if not when:
        return True
    for flag, expected in when.get("flags", {}).items():
        if _get_flag(state, flag) != expected:
            return False
    for flag in when.get("all_flags", []):
        if not bool(_get_flag(state, flag)):
            return False
    any_flags = when.get("any_flags", [])
    if any_flags and not any(bool(_get_flag(flag_state := state, flag)) for flag in any_flags):
        return False
    for flag in when.get("missing_flags", []):
        if bool(_get_flag(state, flag)):
            return False
    return True

class ScenarioScriptExecutor:
    """Executes the v0.6 declarative scene scripting DSL.

    The executor is intentionally side-effect-light: it mutates simple flag state
    only when asked and returns all other effects for owning layers to commit.
    """

    def execute(self, script: ScenarioScript, state: dict[str, Any], hook: str = "on_enter") -> ScenarioResult:
        result = ScenarioResult(script_id=script.script_id, hook=hook)
        for index, step in enumerate(script.steps_for_hook(hook), start=1):
            step_id = f"{hook}.{index}:{step.op}"
            if not _condition_matches(state, step.when):
                result.skipped_steps.append(step_id)
                continue
            try:
                self._execute_step(step, state, result)
                result.executed_steps.append(step_id)
                result.audit_events.append({"event_type": "scenario_step", "script_id": script.script_id, "hook": hook, "op": step.op})
            except Exception as exc:
                result.errors.append(f"{step_id}: {exc}")
        return result

    def execute_on_enter(self, script: ScenarioScript, state: dict[str, Any]) -> ScenarioResult:
        return self.execute(script, state, "on_enter")

    def _execute_step(self, step: ScenarioStep, state: dict[str, Any], result: ScenarioResult) -> None:
        op = step.op
        args = step.args
        if op == "set_flag":
            flag = args.get("flag") or args.get("value")
            value = args.get("value", True) if "flag" in args else True
            _set_flag(state, str(flag), value)
            result.mutations.append({"path": f"module.world_flags.{flag}", "value": value})
        elif op == "clear_flag":
            flag = args.get("flag") or args.get("value")
            _set_flag(state, str(flag), False)
            result.mutations.append({"path": f"module.world_flags.{flag}", "value": False})
        elif op == "reveal":
            result.knowledge_effects.append(dict(args))
            result.mutations.append({"knowledge": dict(args)})
        elif op == "narrate":
            result.narration.append(str(args.get("text") or args.get("value") or args.get("block_id") or ""))
        elif op == "checkpoint":
            result.checkpoints.append(str(args.get("label") or args.get("value")))
        elif op == "transition":
            milestone_id = str(args.get("milestone_id") or args.get("value"))
            _set_flag(state, "current_milestone", milestone_id)
            result.transitions.append(milestone_id)
            result.mutations.append({"path": "module.world_flags.current_milestone", "value": milestone_id})
        elif op == "trigger_scene":
            result.transitions.append(str(args.get("scene_id") or args.get("value")))
        elif op == "add_item":
            result.inventory_effects.append({"op": "add_item", **args})
        elif op == "remove_item":
            result.inventory_effects.append({"op": "remove_item", **args})
        elif op == "move_actor":
            result.map_effects.append({"op": "move_actor", **args})
        elif op == "damage_actor":
            result.mutations.append({"op": "damage_actor", **args})
        elif op == "heal_actor":
            result.mutations.append({"op": "heal_actor", **args})
        elif op == "start_escape_mode":
            mode = str(args.get("mode") or args.get("value") or "escape")
            _set_flag(state, "escape_mode_active", True)
            result.transitions.append(mode)
            result.mutations.append({"path": "module.world_flags.escape_mode_active", "value": True})
        elif op == "run_named_script":
            result.audit_events.append({"event_type": "named_script_requested", "name": args.get("name") or args.get("value")})
        else:
            raise ValueError(f"Unsupported scenario DSL op: {op}")
