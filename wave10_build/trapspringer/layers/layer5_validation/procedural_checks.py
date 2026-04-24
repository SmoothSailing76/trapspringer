from trapspringer.schemas.actions import Action


def check_procedural_legality(action: Action, context: dict) -> tuple[bool, str | None]:
    mode = context.get("mode") or action.context.mode
    # Preserve a permissive exploration smoke path for early skeleton tests while
    # keeping Event 1 combat constrained to the MVP action set.
    if mode == "exploration" and action.action_type in {"inspect", "search", "look", "wait"}:
        return True, None
    if mode not in {"combat", "combat_opening", "setup"}:
        return False, f"Action {action.action_type} is not supported in mode {mode}."
    if action.action_type not in {"melee_attack", "move", "wait"}:
        return False, f"{action.action_type} is not available in this first combat slice."
    return True, None
