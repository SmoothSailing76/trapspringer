"""v0.4 compact AD&D 1e rules facade.

This module is intentionally table-driven and deterministic-friendly.  It is
not a full reproduction of every AD&D 1e table; it is the v0.4 gameplay facade
used by Trapspringer to make common DL1 procedures explicit, auditable, and
capability-aware instead of being hidden in scene scripts.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from trapspringer.services.random_service import RandomService, RollRecord

CLASS_GROUPS = {
    "fighter": "warrior",
    "ranger": "warrior",
    "paladin": "warrior",
    "cleric": "priest",
    "druid": "priest",
    "magic-user": "wizard",
    "mage": "wizard",
    "illusionist": "wizard",
    "thief": "rogue",
    "assassin": "rogue",
    "monster": "monster",
}

# Compact THAC0-style approximation for AD&D 1e class progressions.
# Used to centralize and document the previous MVP attack target logic.
BASE_THAC0 = {
    "warrior": [(1, 20), (3, 18), (5, 16), (7, 14), (9, 12), (11, 10)],
    "priest": [(1, 20), (4, 18), (7, 16), (10, 14), (13, 12)],
    "rogue": [(1, 20), (5, 18), (9, 16), (13, 14)],
    "wizard": [(1, 20), (6, 18), (11, 16)],
    "monster": [(1, 19), (2, 18), (4, 16), (6, 14), (8, 12), (10, 10)],
}

SAVE_TABLE = {
    "warrior": {
        1: {"death": 14, "wand": 15, "paralysis": 16, "breath": 17, "spell": 17},
        5: {"death": 11, "wand": 12, "paralysis": 13, "breath": 13, "spell": 14},
        9: {"death": 8, "wand": 9, "paralysis": 10, "breath": 9, "spell": 11},
    },
    "priest": {
        1: {"death": 10, "wand": 14, "paralysis": 13, "breath": 16, "spell": 15},
        5: {"death": 8, "wand": 12, "paralysis": 11, "breath": 14, "spell": 12},
        9: {"death": 5, "wand": 9, "paralysis": 8, "breath": 11, "spell": 9},
    },
    "rogue": {
        1: {"death": 13, "wand": 14, "paralysis": 13, "breath": 16, "spell": 15},
        5: {"death": 11, "wand": 12, "paralysis": 11, "breath": 14, "spell": 13},
        9: {"death": 9, "wand": 10, "paralysis": 9, "breath": 12, "spell": 11},
    },
    "wizard": {
        1: {"death": 14, "wand": 11, "paralysis": 13, "breath": 15, "spell": 12},
        6: {"death": 13, "wand": 9, "paralysis": 11, "breath": 13, "spell": 10},
        11: {"death": 11, "wand": 7, "paralysis": 9, "breath": 11, "spell": 8},
    },
    "monster": {
        1: {"death": 14, "wand": 15, "paralysis": 16, "breath": 17, "spell": 17},
        4: {"death": 12, "wand": 13, "paralysis": 14, "breath": 15, "spell": 15},
        8: {"death": 10, "wand": 11, "paralysis": 12, "breath": 13, "spell": 13},
    },
}

SPELLS = {
    "magic_missile": {"level": 1, "damage": "1d4", "bonus": 1, "save": None, "type": "damage"},
    "sleep": {"level": 1, "hit_dice_affected": "2d4", "save": None, "type": "control"},
    "web": {"level": 2, "save": "spell", "type": "restrain", "duration_turns": 2},
    "cure_light_wounds": {"level": 1, "healing": "1d8", "bonus": 0, "type": "healing"},
    "darkness": {"level": 2, "save": None, "type": "vision"},
}

TURN_UNDEAD_MATRIX = {
    # result values: None = no effect, "T" = turned, "D" = destroyed, int = d20 target
    1: {"skeleton": 10, "zombie": 13, "ghoul": 16, "wight": 19},
    3: {"skeleton": 4, "zombie": 7, "ghoul": 10, "wight": 13},
    5: {"skeleton": "T", "zombie": "T", "ghoul": 4, "wight": 7},
    7: {"skeleton": "D", "zombie": "T", "ghoul": "T", "wight": 4},
    9: {"skeleton": "D", "zombie": "D", "ghoul": "T", "wight": "T"},
}

ITEM_SAVE_TARGETS = {
    "paper": {"acid": 17, "fire": 19, "crushing": 16, "lightning": 19},
    "wood": {"acid": 13, "fire": 17, "crushing": 11, "lightning": 18},
    "metal": {"acid": 7, "fire": 14, "crushing": 6, "lightning": 12},
    "stone": {"acid": 10, "fire": 11, "crushing": 7, "lightning": 14},
    "magical_item": {"acid": 5, "fire": 7, "crushing": 4, "lightning": 6},
}

@dataclass(slots=True)
class RuleCheck:
    rule_id: str
    status: str
    success: bool
    target: int | str | None = None
    roll: dict[str, Any] | None = None
    result: str | None = None
    notes: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def class_group(actor: Any) -> str:
    raw = (getattr(actor, "character_class", None) or getattr(actor, "actor_type", None) or "monster").lower()
    return CLASS_GROUPS.get(raw, "monster" if getattr(actor, "team", None) == "enemy" else "warrior")


def _level_band(table: dict[int, Any], level: int) -> Any:
    key = max(k for k in table if level >= k)
    return table[key]


def thac0_for(actor: Any) -> int:
    group = class_group(actor)
    level = int(getattr(actor, "level", 1) or 1)
    return int(_level_band(dict(BASE_THAC0.get(group, BASE_THAC0["monster"])), level))


def attack_target(actor: Any, target: Any, modifiers: dict[str, int] | None = None) -> RuleCheck:
    modifiers = modifiers or {}
    target_ac = int(getattr(target, "ac", 10))
    needed = max(2, min(20, thac0_for(actor) - target_ac - sum(modifiers.values())))
    return RuleCheck("attack_matrix", "implemented", True, target=needed, metadata={"target_ac": target_ac, "thac0": thac0_for(actor), "modifiers": modifiers})


def roll_attack(actor: Any, target: Any, rng: RandomService, modifiers: dict[str, int] | None = None, purpose: str | None = None) -> RuleCheck:
    base = attack_target(actor, target, modifiers)
    roll = rng.roll_dice("1d20", purpose or f"attack:{getattr(actor, 'actor_id', 'actor')}->{getattr(target, 'actor_id', 'target')}")
    base.roll = asdict(roll)
    base.success = roll.total >= int(base.target)
    base.result = "hit" if base.success else "miss"
    return base


def saving_throw_target(actor: Any, category: str) -> RuleCheck:
    category = category.lower().replace(" ", "_")
    aliases = {"poison": "death", "death_magic": "death", "petrification": "paralysis", "rod_staff_wand": "wand", "breath_weapon": "breath"}
    category = aliases.get(category, category)
    group = class_group(actor)
    level = int(getattr(actor, "level", 1) or 1)
    band = _level_band(SAVE_TABLE.get(group, SAVE_TABLE["monster"]), level)
    target = int(band.get(category, band["spell"]))
    return RuleCheck("saving_throw", "implemented", True, target=target, metadata={"category": category, "class_group": group, "level": level})


def roll_saving_throw(actor: Any, category: str, rng: RandomService, modifiers: dict[str, int] | None = None) -> RuleCheck:
    modifiers = modifiers or {}
    check = saving_throw_target(actor, category)
    roll = rng.roll_dice("1d20", f"save:{getattr(actor, 'actor_id', 'actor')}:{category}", modifiers=modifiers)
    check.roll = asdict(roll)
    check.success = roll.total >= int(check.target)
    check.result = "saved" if check.success else "failed"
    check.metadata["modifiers"] = modifiers
    return check


def initiative(rng: RandomService, side: str = "party", modifier: int = 0) -> RuleCheck:
    roll = rng.roll_dice("1d6", f"initiative:{side}", modifiers={"modifier": modifier} if modifier else {})
    return RuleCheck("initiative", "implemented", True, target="higher_wins", roll=asdict(roll), result=str(roll.total), metadata={"side": side})


def surprise(rng: RandomService, side: str = "party", threshold: int = 2) -> RuleCheck:
    roll = rng.roll_dice("1d6", f"surprise:{side}")
    surprised = roll.total <= threshold
    return RuleCheck("surprise", "implemented", not surprised, target=threshold, roll=asdict(roll), result="surprised" if surprised else "not_surprised", metadata={"segments_lost": max(0, threshold - roll.total + 1) if surprised else 0})


def morale_check(rng: RandomService, morale_score: int, situation_modifier: int = 0, group_id: str = "group") -> RuleCheck:
    roll = rng.roll_dice("2d6", f"morale:{group_id}", modifiers={"situation": situation_modifier} if situation_modifier else {})
    success = roll.total <= morale_score
    return RuleCheck("morale", "implemented", success, target=morale_score, roll=asdict(roll), result="holds" if success else "breaks")


def reaction_check(rng: RandomService, modifier: int = 0, npc_id: str = "npc") -> RuleCheck:
    roll = rng.roll_dice("2d10", f"reaction:{npc_id}", modifiers={"modifier": modifier} if modifier else {})
    total = roll.total
    if total <= 5:
        result = "hostile"
    elif total <= 8:
        result = "unfriendly"
    elif total <= 12:
        result = "uncertain"
    elif total <= 16:
        result = "friendly"
    else:
        result = "helpful"
    return RuleCheck("reaction", "implemented", result in {"friendly", "helpful"}, target="2d10 reaction band", roll=asdict(roll), result=result)


def turn_undead(cleric: Any, undead_type: str, rng: RandomService) -> RuleCheck:
    level = int(getattr(cleric, "level", 1) or 1)
    band = _level_band(TURN_UNDEAD_MATRIX, level)
    target = band.get(undead_type.lower())
    if target is None:
        return RuleCheck("turn_undead", "partial", False, target=None, result="no_effect", notes="Undead type not in compact v0.4 matrix.")
    if target in {"T", "D"}:
        return RuleCheck("turn_undead", "implemented", True, target=target, result="destroyed" if target == "D" else "turned")
    roll = rng.roll_dice("1d20", f"turn_undead:{getattr(cleric, 'actor_id', 'cleric')}:{undead_type}")
    success = roll.total >= int(target)
    return RuleCheck("turn_undead", "implemented", success, target=int(target), roll=asdict(roll), result="turned" if success else "no_effect")


def encumbrance_move(base_move: int, carried_weight_gp: int, strength: int = 10) -> RuleCheck:
    allowance = 350 + max(0, strength - 10) * 100
    if carried_weight_gp <= allowance:
        move = base_move
        band = "unencumbered"
    elif carried_weight_gp <= allowance * 2:
        move = max(3, base_move - 3)
        band = "light"
    elif carried_weight_gp <= allowance * 3:
        move = max(3, base_move - 6)
        band = "heavy"
    else:
        move = max(1, base_move - 9)
        band = "severe"
    return RuleCheck("encumbrance", "partial", True, target=move, result=band, metadata={"base_move": base_move, "carried_weight_gp": carried_weight_gp, "strength": strength})


def item_save(item_material: str, attack_form: str, rng: RandomService, magical_bonus: int = 0) -> RuleCheck:
    table = ITEM_SAVE_TARGETS.get(item_material, ITEM_SAVE_TARGETS["wood"])
    target = int(table.get(attack_form, table.get("fire", 17)))
    roll = rng.roll_dice("1d20", f"item_save:{item_material}:{attack_form}", modifiers={"magic": magical_bonus} if magical_bonus else {})
    success = roll.total >= target
    return RuleCheck("item_saving_throw", "partial", success, target=target, roll=asdict(roll), result="survives" if success else "destroyed")


def xp_award(monster_xp: int = 0, treasure_gp: int = 0, party_size: int = 1) -> RuleCheck:
    total = int(monster_xp) + int(treasure_gp)
    share = total // max(1, int(party_size))
    return RuleCheck("xp_treasure", "partial", True, target=share, result="xp_awarded", metadata={"total_xp": total, "party_size": party_size, "share": share})
