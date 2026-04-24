from __future__ import annotations

from trapspringer.schemas.party import DiscussionLine, Proposal


def choose_caller(active_actor_ids: list[str], fallback: str = "PC_TANIS") -> str | None:
    if fallback in active_actor_ids:
        return fallback
    return active_actor_ids[0] if active_actor_ids else None


def summarize_for_caller(lines: list[DiscussionLine] | list[dict[str, object]], proposals: list[Proposal] | None = None, caller_id: str | None = "PC_TANIS") -> str | None:
    proposals = proposals or []
    if proposals:
        top = sorted(proposals, key=lambda p: p.priority, reverse=True)[:3]
        intents = []
        for proposal in top:
            if proposal.intent_tags:
                intents.append(proposal.intent_tags[0].replace("_", " "))
        if intents:
            return f"Caller summary: {', '.join(intents)}; keep the party coordinated."
    if lines:
        return "Caller summary: hold formation, use caution, and make declarations clearly."
    return None
