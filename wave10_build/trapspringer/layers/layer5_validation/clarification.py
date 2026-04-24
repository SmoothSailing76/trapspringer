from trapspringer.schemas.actions import Action


def needs_clarification(action: Action, context: dict) -> tuple[bool, str | None]:
    if action.action_type == "melee_attack" and (action.target is None or not action.target.id):
        return True, "Which enemy are you attacking?"
    return False, None
