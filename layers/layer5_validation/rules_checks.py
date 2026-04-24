from trapspringer.schemas.actions import Action


def check_rules_legality(action: Action, context: dict) -> tuple[bool, str | None]:
    # Wave 2 keeps rules legality intentionally narrow.
    return True, None
