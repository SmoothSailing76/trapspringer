"""Small source-backed rule/query facade for the Event 1 vertical slice.

The full project will replace these hard-coded MVP lookups with table loaders
from the PHB/DMG/MM/DL1 manifests. These functions still return structured
answers with source locators so higher layers do not inline rule constants.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

COMMON_RULE_QUERIES = {
    "attack_matrix": "What attack matrix applies?",
    "saving_throw": "What saving throw applies?",
    "dragon_fear": "How is dragon fear resolved?",
    "dl1_event_timing": "When does this DL1 event trigger?",
    "item_restriction": "What item restriction applies?",
}


@dataclass(slots=True)
class RuleQueryResult:
    query: str
    status: str
    answer: Any
    source_id: str
    locator: str
    notes: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def attack_target_number(attacker: Any, target: Any) -> RuleQueryResult:
    """Return the MVP d20 target number used by Event 1 combat.

    This intentionally preserves the Wave 2 approximation so replay behavior
    remains stable, while centralizing it behind the authority/query facade.
    """
    if getattr(attacker, "team", None) == "party":
        level = int(getattr(attacker, "level", 1) or 1)
        base = 20 - level
        needed = max(2, base - int(getattr(target, "ac", 10)))
    else:
        needed = max(2, 20 - int(getattr(target, "ac", 10)) - 1)
    return RuleQueryResult(
        query="attack_matrix",
        status="binding_mvp",
        answer=needed,
        source_id="DMG",
        locator="DMG_02_COMBAT_TABLES / Event 1 MVP approximation",
        notes="MVP Event 1 matrix approximation; replace with full AD&D tables in later wave.",
        metadata={"target_ac": getattr(target, "ac", None), "attacker_level": getattr(attacker, "level", None)},
    )


def weapon_damage_dice(actor: Any) -> RuleQueryResult:
    inv = " ".join(getattr(actor, "inventory", []) or [])
    if "axe" in inv or "hand_axe" in inv:
        dice = "1d6"
    elif "hoopak" in inv:
        dice = "1d6"
    elif "staff_of_magius" in inv:
        dice = "1d8"
    else:
        dice = getattr(actor, "damage", "1d6") if getattr(actor, "team", None) == "enemy" else "1d8"
    return RuleQueryResult(
        query="damage_basis",
        status="binding_mvp",
        answer=dice,
        source_id="PHB/MM/DL1",
        locator="PHB weapons / DL1 Event 1 stat blocks / MVP equipment mapping",
        notes="MVP weapon mapping for Event 1.",
    )


def event1_script(script_name: str) -> RuleQueryResult:
    scripts = {
        "toede_opening": "Fewmaster Toede demands the blue crystal staff, orders the attack, and flees immediately.",
        "hobgoblin_behavior": "The ten Event 1 hobgoblins fight to the death.",
        "captured_hobgoblin_knowledge": "Captured hobgoblins know only that they were ordered to search the road at night for a blue crystal staff.",
    }
    return RuleQueryResult(
        query=f"dl1_event1_script:{script_name}",
        status="binding",
        answer=scripts.get(script_name),
        source_id="DL1",
        locator="DL1_02_EVENTS.md / EVENT 1: The Adventure Begins",
    )


def query_rule(name: str, **kwargs: Any) -> RuleQueryResult:
    if name == "attack_matrix":
        return attack_target_number(kwargs["attacker"], kwargs["target"])
    if name == "damage_basis":
        return weapon_damage_dice(kwargs["actor"])
    if name.startswith("event1_") or name in {"toede_opening", "hobgoblin_behavior", "captured_hobgoblin_knowledge"}:
        return event1_script(name.replace("event1_", ""))
    return RuleQueryResult(name, "unresolved", None, "UNKNOWN", "UNKNOWN", notes="No MVP rule query implemented.")
