from __future__ import annotations

from trapspringer.schemas.party import DiscussionLine, Proposal


class CallerState:
    """Tracks caller authority and how often the table accepts summaries."""

    def __init__(self, caller_actor_id: str = "PC_TANIS") -> None:
        self.caller_actor_id = caller_actor_id
        self.authority_strength = 0.72
        self.accepted_summaries = 0
        self.contested_summaries = 0

    def apply_outcome(self, accepted: bool) -> None:
        if accepted:
            self.accepted_summaries += 1
            self.authority_strength = min(0.95, self.authority_strength + 0.03)
        else:
            self.contested_summaries += 1
            self.authority_strength = max(0.25, self.authority_strength - 0.06)

    def to_dict(self) -> dict[str, object]:
        return {
            "caller_actor_id": self.caller_actor_id,
            "authority_strength": round(self.authority_strength, 2),
            "accepted_summaries": self.accepted_summaries,
            "contested_summaries": self.contested_summaries,
        }


def summarize_for_caller(lines: list[DiscussionLine], proposals: list[Proposal]) -> str | None:
    if not proposals and not lines:
        return None
    tags = [tag for p in proposals for tag in p.intent_tags]
    if "escape" in tags:
        return "Caller summary: no debate; move now, keep the wounded between the front and rear guards."
    if "guard_goldmoon" in tags or "mission" in tags:
        return "Caller summary: protect the staff-bearer and keep moving toward the objective."
    if "scout" in tags and "caution" in tags:
        return "Caller summary: scout only as far as the group can cover, then report back before anyone commits."
    if "risk" in tags:
        return "Caller summary: allow the risky idea only if a retreat path stays open."
    if proposals:
        top = max(proposals, key=lambda p: p.priority)
        return f"Caller summary: {top.spoken_text}"
    return "Caller summary: hold formation and wait for a clear opening."


def apply_caller_convergence(caller_state: CallerState, dissent: list[str]) -> dict[str, object]:
    contested = bool(dissent) and caller_state.authority_strength < 0.82
    caller_state.apply_outcome(not contested)
    return {"accepted": not contested, "caller_state": caller_state.to_dict(), "dissent_count": len(dissent)}
