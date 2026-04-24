from trapspringer.schemas.actions import Action, ActionContext, ActionTarget, MovementComponent
from trapspringer.schemas.declarations import Declaration


def normalize_action(action: Action) -> Action:
    return action


def parse_user_declaration(text: str, actor_id: str, action_id: str = "ACT-USER-1", mode: str = "combat") -> Declaration:
    """Very small Wave 2 parser for Event 1 combat input."""
    raw = text.strip()
    low = raw.lower()
    context = ActionContext(mode=mode, phase="declaration", scene_id="DL1_EVENT_1_AMBUSH")

    if any(w in low for w in ["wait", "hold", "ready"]):
        action = Action(action_id, actor_id, "wait", context, spoken_text=raw)
        return Declaration(f"DEC-{action_id}", actor_id, raw, action)

    if low.startswith("move") or "move to" in low or "go to" in low:
        dest = "road_center_party"
        if "left" in low:
            dest = "left_woodline"
        elif "right" in low:
            dest = "right_woodline"
        elif "road" in low or "center" in low:
            dest = "road_center_party"
        elif "toede" in low or "rider" in low:
            dest = "toede_front"
        action = Action(
            action_id,
            actor_id,
            "move",
            context,
            target=ActionTarget("zone", dest),
            movement_component=MovementComponent(True, dest),
            spoken_text=raw,
        )
        return Declaration(f"DEC-{action_id}", actor_id, raw, action)

    # Default to melee attack.
    target = "nearest_enemy"
    if "toede" in low or "rider" in low or "pony" in low:
        target = "NPC_TOEDE"
    elif "hobgoblin" in low or "nearest" in low or "enemy" in low:
        target = "nearest_enemy"
    action = Action(
        action_id,
        actor_id,
        "melee_attack",
        context,
        target=ActionTarget("actor", target),
        spoken_text=raw,
    )
    return Declaration(f"DEC-{action_id}", actor_id, raw, action)
