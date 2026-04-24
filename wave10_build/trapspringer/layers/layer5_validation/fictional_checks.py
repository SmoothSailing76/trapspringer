from trapspringer.schemas.actions import Action


def _nearest_enemy(action: Action, context: dict) -> str | None:
    state = context.get("state", {})
    map_service = context.get("map_service")
    chars = state.get("characters", {}) if isinstance(state, dict) else {}
    for aid, c in chars.items():
        if getattr(c, "team", None) != "enemy" or not getattr(c, "is_active", False):
            continue
        if aid == "NPC_TOEDE" and state.get("module") and state["module"].world_flags.get("toede_fled"):
            continue
        if not map_service or map_service.query_visibility({"scene_id": action.context.scene_id or "DL1_EVENT_1_AMBUSH", "observer": action.actor_id, "target": aid}).payload.get("visible"):
            return aid
    return None


def check_fictional_legality(action: Action, context: dict) -> tuple[bool, str | None]:
    state = context.get("state", {})
    chars = state.get("characters", {}) if isinstance(state, dict) else {}
    actor = chars.get(action.actor_id)
    if actor is None:
        # Allow pure smoke/contract validation calls that do not provide a live state.
        if not chars and action.context.mode == "exploration" and action.action_type in {"inspect", "search", "look", "wait"}:
            return True, None
        return False, f"Unknown actor {action.actor_id}."
    if not getattr(actor, "is_active", False):
        return False, f"{actor.name} cannot act right now."

    map_service = context.get("map_service")
    if action.action_type == "wait":
        return True, None

    if action.action_type == "move":
        dest = action.target.id if action.target else None
        if not dest:
            return False, "No destination was declared."
        if map_service and not map_service.query_reachability({"scene_id": action.context.scene_id or "DL1_EVENT_1_AMBUSH", "actor": action.actor_id, "target_zone": dest}).payload.get("reachable"):
            return False, f"{actor.name} cannot reach {dest} from here this round."
        return True, None

    if action.action_type == "melee_attack":
        target_id = action.target.id if action.target else None
        if target_id == "nearest_enemy":
            target_id = _nearest_enemy(action, context)
            if target_id is None:
                return False, "No visible enemy is available to attack."
            action.extra["resolved_target_id"] = target_id
        if target_id == "NPC_TOEDE" and state.get("module") and state["module"].world_flags.get("toede_fled"):
            return False, "Toede has already fled into the woods."
        target = chars.get(target_id)
        if target is None or not getattr(target, "is_active", False):
            return False, "That target is not available."
        if map_service and not map_service.query_visibility({"scene_id": action.context.scene_id or "DL1_EVENT_1_AMBUSH", "observer": action.actor_id, "target": target_id}).payload.get("visible"):
            return False, "You cannot clearly see that target."
        # In this abstract first slice, line of sight within adjacent zones permits a charge/engagement.
        action.extra["resolved_target_id"] = target_id
        return True, None

    return True, None
