from trapspringer.schemas.resolution import ResolutionResult


def render_combat_results(results: list[ResolutionResult]) -> str:
    lines = []
    for result in results:
        if result.public_outcome and result.public_outcome.narration:
            lines.append(result.public_outcome.narration)
    return "\n".join(lines)


def render_round_prompt(round_no: int = 1) -> str:
    return f"Declare actions for combat round {round_no}: movement, attacks, or waiting."


def render_invalid_action(reason: str | None) -> str:
    return reason or "That action is not valid as declared."
