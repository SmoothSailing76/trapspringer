"""Resolve a `search` action against Layer 2 hidden facts.

AD&D 1e search (PHB pp. 16-17):
  - Default: 1-in-6 per round of careful searching (DMG).
  - Elf / half-elf actively searching for a secret door: 2-in-6.
  - Elf / half-elf searching for a concealed door: 3-in-6.
  - Dwarves and gnomes have detection bonuses for stonework / structural
    phenomena; the categories below approximate the printed probabilities
    on a d6 roll for engine uniformity.

The resolver finds candidate KnowledgeFacts whose `discovery_conditions`
list contains the action's `target_kind`, then rolls a single d6 against
the threshold. On success it emits a knowledge_effect for the orchestrator
to commit through Layer 2.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from trapspringer.schemas.actions import Action
from trapspringer.schemas.resolution import PrivateOutcome, PublicOutcome, ResolutionResult
from trapspringer.services.random_service import RandomService

# (race, category) -> highest d6 roll that succeeds.
_RACIAL_BONUSES: dict[tuple[str, str], int] = {
    ("elf", "secret_door"): 2,
    ("elf", "concealed_door"): 3,
    ("half_elf", "secret_door"): 2,
    ("half_elf", "concealed_door"): 3,
    ("dwarf", "stonework_trap"): 3,
    ("dwarf", "sliding_wall"): 4,
    ("gnome", "unsafe_structure"): 4,
}

# Map free-text discovery condition tokens to a generic search category
# so racial bonuses can be looked up uniformly.
_CONDITION_CATEGORY: dict[str, str] = {
    "spot_hidden_draconians": "secret_door",
    "find_secret_door": "secret_door",
    "find_concealed_door": "concealed_door",
    "spot_stonework_trap": "stonework_trap",
    "detect_sliding_wall": "sliding_wall",
    "detect_unsafe_structure": "unsafe_structure",
}


def _actor_race(actor: Any) -> str:
    return (getattr(actor, "race", None) or "").lower().replace("-", "_")


def _search_threshold(actor: Any, target_kind: str) -> tuple[int, str]:
    category = _CONDITION_CATEGORY.get(target_kind, target_kind)
    race = _actor_race(actor)
    bonus = _RACIAL_BONUSES.get((race, category))
    if bonus is not None:
        return bonus, f"PHB pp.16-17 racial detection: {race} {category}"
    return 1, "DMG default 1-in-6 per round of careful search"


def _candidate_facts(knowledge_service: Any, target_kind: str, target_area: str | None) -> list[Any]:
    out = []
    for fact in knowledge_service.facts.all():
        if target_kind not in fact.discovery_conditions:
            continue
        if "PARTY" in fact.known_by or "public_table" in fact.known_by:
            continue
        if target_area and fact.source and target_area not in fact.source:
            continue
        out.append(fact)
    return out


def resolve_search(action: Action, state: dict, knowledge_service: Any, rng: RandomService) -> ResolutionResult:
    chars = state["characters"]
    actor = chars.get(action.actor_id)
    if actor is None or not getattr(actor, "is_active", False):
        return ResolutionResult(
            f"RES-{action.action_id}", "no_effect",
            PrivateOutcome({"actor_inactive": True}),
            PublicOutcome(None),
        )

    target_kind = str(action.extra.get("target_kind") or "")
    target_area = action.extra.get("target_area_id")

    if knowledge_service is None or not target_kind:
        missing = "knowledge_service" if knowledge_service is None else "target_kind"
        return ResolutionResult(
            f"RES-{action.action_id}", "no_effect",
            PrivateOutcome({"missing": missing}),
            PublicOutcome(f"{actor.name} pauses, unsure what to look for."),
        )

    candidates = _candidate_facts(knowledge_service, target_kind, target_area)
    if not candidates:
        return ResolutionResult(
            f"RES-{action.action_id}", "resolved",
            PrivateOutcome({"target_kind": target_kind, "candidates": 0}),
            PublicOutcome(f"{actor.name} searches carefully but finds nothing of note."),
        )

    threshold, basis = _search_threshold(actor, target_kind)
    roll = rng.roll_dice("1d6", f"search:{action.actor_id}:{target_kind}")
    success = roll.total <= threshold

    private = {
        "target_kind": target_kind,
        "candidate_count": len(candidates),
        "search_roll": asdict(roll),
        "threshold": threshold,
        "rule_basis": basis,
        "success": success,
    }

    if not success:
        return ResolutionResult(
            f"RES-{action.action_id}", "resolved",
            PrivateOutcome(private),
            PublicOutcome(f"{actor.name} searches carefully but finds nothing this round."),
        )

    discovered = candidates[0]
    private["discovered_fact_id"] = discovered.fact_id

    return ResolutionResult(
        f"RES-{action.action_id}", "resolved",
        PrivateOutcome(private),
        PublicOutcome(f"{actor.name} discovers something hidden: {discovered.proposition}"),
        knowledge_effects=[{
            "fact_id": discovered.fact_id,
            "proposition": discovered.proposition,
            "discovered_by": "PARTY",
            "visibility_after": "party_known",
        }],
    )
