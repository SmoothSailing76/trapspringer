"""Source-backed rule/query facade for Trapspringer v0.4."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trapspringer.rules import adnd1e_v04

COMMON_RULE_QUERIES = {
    "attack_matrix": "What attack matrix applies?",
    "saving_throw": "What saving throw applies?",
    "dragon_fear": "How is dragon fear resolved?",
    "dl1_event_timing": "When does this DL1 event trigger?",
    "item_restriction": "What item restriction applies?",
    "initiative": "How is initiative rolled?",
    "surprise": "How is surprise resolved?",
    "morale": "How is morale checked?",
    "reaction": "How is NPC reaction checked?",
    "turn_undead": "How is undead turning resolved?",
    "encumbrance": "How does carried weight affect movement?",
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


def attack_target_number(attacker: Any, target: Any, modifiers: dict[str, int] | None = None) -> RuleQueryResult:
    check = adnd1e_v04.attack_target(attacker, target, modifiers)
    return RuleQueryResult(
        "attack_matrix", "binding_v04", check.target, "DMG",
        "DMG combat matrices / v0.4 compact THAC0 facade",
        "v0.4 class-group attack facade; exact printed matrix values may be substituted by content packs.",
        check.metadata,
    )


def weapon_damage_dice(actor: Any) -> RuleQueryResult:
    inv = " ".join(getattr(actor, "inventory", []) or []).lower()
    if "longbow" in inv or "bow" in inv:
        dice = "1d6"
    elif "axe" in inv or "hand_axe" in inv:
        dice = "1d6"
    elif "hoopak" in inv:
        dice = "1d6"
    elif "staff_of_magius" in inv:
        dice = "1d8"
    elif "staff" in inv:
        dice = "1d6"
    elif getattr(actor, "team", None) == "enemy":
        dice = getattr(actor, "damage", "1d6")
    else:
        dice = "1d8"
    return RuleQueryResult("damage_basis", "binding_v04", dice, "PHB/MM/DL1", "PHB weapons / MM stat blocks / DL1 equipment facade")


def saving_throw(actor: Any, category: str) -> RuleQueryResult:
    check = adnd1e_v04.saving_throw_target(actor, category)
    return RuleQueryResult("saving_throw", "binding_v04", check.target, "DMG", "DMG saving throw matrices / v0.4 compact class-group table", metadata=check.metadata)


def spell_definition(spell_name: str) -> RuleQueryResult:
    key = spell_name.lower().replace(" ", "_")
    answer = adnd1e_v04.SPELLS.get(key)
    return RuleQueryResult(f"spell:{key}", "binding_v04" if answer else "unresolved", answer, "PHB/DL1", "PHB spell descriptions / DL1 supported spell subset")


def event1_script(script_name: str) -> RuleQueryResult:
    scripts = {
        "toede_opening": "Fewmaster Toede demands the blue crystal staff, orders the attack, and flees immediately.",
        "hobgoblin_behavior": "The ten Event 1 hobgoblins fight to the death.",
        "captured_hobgoblin_knowledge": "Captured hobgoblins know only that they were ordered to search the road at night for a blue crystal staff.",
    }
    return RuleQueryResult(f"dl1_event1_script:{script_name}", "binding", scripts.get(script_name), "DL1", "DL1_02_EVENTS.md / EVENT 1: The Adventure Begins")


def query_rule(name: str, **kwargs: Any) -> RuleQueryResult:
    if name == "attack_matrix":
        return attack_target_number(kwargs["attacker"], kwargs["target"], kwargs.get("modifiers"))
    if name == "damage_basis":
        return weapon_damage_dice(kwargs["actor"])
    if name == "saving_throw":
        return saving_throw(kwargs["actor"], kwargs.get("category", "spell"))
    if name == "spell_definition":
        return spell_definition(kwargs["spell_name"])
    if name.startswith("event1_") or name in {"toede_opening", "hobgoblin_behavior", "captured_hobgoblin_knowledge"}:
        return event1_script(name.replace("event1_", ""))
    return RuleQueryResult(name, "unresolved", None, "UNKNOWN", "UNKNOWN", notes="No v0.4 rule query implemented.")
