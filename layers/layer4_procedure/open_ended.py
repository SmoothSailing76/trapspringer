from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class OpenEndedIntent:
    """Normalized representation of an unexpected/non-mainline player choice.

    This is deliberately lightweight: it gives the orchestrator a safe routing
    point without pretending that every possible table idea is already modeled.
    """

    intent_type: str
    confidence: float = 0.5
    actor_id: str | None = None
    target: str | None = None
    raw_text: str = ""
    tags: list[str] = field(default_factory=list)
    requires_ruling: bool = False


def classify_open_ended_intent(text: str, actor_id: str | None = None, scene_id: str | None = None) -> OpenEndedIntent:
    raw = (text or "").strip()
    low = raw.lower()

    # Strategic refusal / avoidance.
    if any(p in low for p in ["refuse", "don't go", "do not go", "avoid xak", "skip xak", "ignore the hook", "leave krynn"]):
        return OpenEndedIntent("refuse_hook", 0.84, actor_id, raw_text=raw, tags=["strategic", "branch"])

    # Retreat and re-entry support.
    if any(p in low for p in ["retreat", "fall back", "withdraw", "run away", "go back", "leave the dungeon", "escape upward"]):
        return OpenEndedIntent("retreat", 0.88, actor_id, raw_text=raw, tags=["movement", "safety"])

    # Party splitting.
    if any(p in low for p in ["split", "scout ahead", "send tasslehoff", "send the thief", "two groups", "separate"]):
        return OpenEndedIntent("split_party", 0.82, actor_id, raw_text=raw, tags=["party_split", "risk"])

    # Prisoner interrogation is distinct from the earlier capture attempt.
    if any(p in low for p in ["interrogate", "question", "ask the prisoner", "ask him", "make him talk"]):
        return OpenEndedIntent("interrogate_prisoner", 0.86, actor_id, target="prisoner", raw_text=raw, tags=["social", "information"])
    if any(p in low for p in ["capture", "take prisoner", "take a", "prisoner", "tie up", "bind", "knock out"]):
        return OpenEndedIntent("take_prisoner", 0.80, actor_id, target="enemy", raw_text=raw, tags=["social", "combat_aftercare"])

    # Key-item loss/destruction edge cases.
    if any(p in low for p in ["drop the staff", "throw away the staff", "throws away", "lose the staff", "break the staff", "destroy the staff"]):
        return OpenEndedIntent("key_item_risk", 0.84, actor_id, target="blue_crystal_staff", raw_text=raw, tags=["key_item", "failure_state"])

    # Search/alternate route probing.
    if any(p in low for p in ["search", "look for another way", "secret", "hidden route", "alternate route", "map the area"]):
        return OpenEndedIntent("search_alternate_route", 0.72, actor_id, raw_text=raw, tags=["exploration", "route"])

    # Camp/rest/time passing.
    if any(p in low for p in ["camp", "rest", "sleep", "set watches", "wait until morning"]):
        return OpenEndedIntent("rest_or_delay", 0.78, actor_id, raw_text=raw, tags=["time", "risk"])

    return OpenEndedIntent("requires_ruling", 0.35, actor_id, raw_text=raw, tags=["unknown"], requires_ruling=True)


def open_ended_policy_response(intent: OpenEndedIntent, state: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a structured policy response for open-ended choices.

    The response does not mutate state. Resolution is handled by Layer 6 and
    committed through Layer 3.
    """
    if intent.intent_type == "requires_ruling":
        return {
            "status": "requires_human_ruling",
            "reason": "The engine cannot safely model this exact action yet.",
            "closest_supported": ["retreat", "split_party", "take_prisoner", "interrogate_prisoner", "search_alternate_route", "rest_or_delay"],
        }
    return {"status": "supported_branch", "intent_type": intent.intent_type, "confidence": intent.confidence, "tags": intent.tags}
