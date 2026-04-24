from __future__ import annotations

from trapspringer.schemas.party import Proposal


def converge_plan(proposals: list[Proposal], caller_id: str | None = "PC_TANIS") -> tuple[str, list[str]]:
    if not proposals:
        return "Caller summary: no strong plan emerges; default to holding formation.", []
    top = sorted(proposals, key=lambda p: p.priority, reverse=True)[:4]
    tags = [tag for proposal in top for tag in proposal.intent_tags]
    dissent: list[str] = []
    if "risk" in tags and "caution" in tags:
        dissent.append("Risky scouting is allowed only with the rest of the group watching for trouble.")
    if "protect_raistlin" in tags and "front_rank" in tags:
        summary = "Caller summary: front rank holds while Caramon protects Raistlin; the scout or staff-bearer acts only with support."
    elif "mission" in tags and "caution" in tags:
        summary = "Caller summary: keep moving toward the quest objective, but advance slowly and do not split the group."
    elif "scout" in tags:
        summary = "Caller summary: let the scout inspect first while the others cover visible approaches."
    else:
        summary = "Caller summary: hold formation and follow the safest high-priority proposal."
    return summary, dissent
