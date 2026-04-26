"""Apply ResourceChange records emitted by Layer 6 resolvers.

Spell and missile resolvers emit ResourceChange(owner, resource_type, delta, note)
on every cast or shot, but until now those records were dropped — meaning
spell slots never decremented and ammunition never depleted.

Supported resource_types:
  - "spell_slot": Vancian — removes one occurrence of the spell name (carried
    in `note`) from actor.spells. Already-expended spells silently no-op so
    the audit shows applied=False without raising.
  - "ammunition": data-model gap — CharacterState has no per-item counts
    (inventory is a category list). Records the intent in the audit but
    does not mutate. Add an inventory-count schema before wiring this up.

Returns a list of audit dicts so the orchestrator can log what actually
got applied vs. skipped (and why).
"""
from __future__ import annotations

from typing import Any

from trapspringer.schemas.resolution import ResourceChange


def _coerce(change: ResourceChange | dict[str, Any]) -> ResourceChange:
    if isinstance(change, ResourceChange):
        return change
    return ResourceChange(
        owner=str(change.get("owner", "")),
        resource_type=str(change.get("resource_type", "")),
        delta=int(change.get("delta", 0)),
        note=change.get("note"),
    )


def _apply_spell_slot(actor: Any, change: ResourceChange) -> dict[str, Any]:
    spell_name = (change.note or "").strip().lower().replace(" ", "_")
    spells = list(getattr(actor, "spells", []) or [])
    if not spell_name:
        return {"owner": change.owner, "resource_type": change.resource_type, "applied": False, "reason": "missing_spell_name"}
    if spell_name not in spells:
        return {"owner": change.owner, "resource_type": change.resource_type, "applied": False, "reason": "spell_already_expended", "spell": spell_name}
    spells.remove(spell_name)
    actor.spells = spells
    return {"owner": change.owner, "resource_type": change.resource_type, "applied": True, "spell": spell_name, "remaining_spells": list(spells)}


def _apply_ammunition(actor: Any, change: ResourceChange) -> dict[str, Any]:
    # CharacterState.inventory is a category list (e.g. ["sword", "bow", "armor"]),
    # not per-item counts. Record the intent but do not mutate; promote to real
    # decrement once an inventory-count schema exists.
    return {
        "owner": change.owner,
        "resource_type": change.resource_type,
        "applied": False,
        "reason": "no_inventory_count_schema",
        "delta": change.delta,
        "note": change.note,
    }


def apply_resource_changes(state: dict[str, Any], changes: list[ResourceChange | dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply each ResourceChange against state and return a per-change audit list."""
    if not changes:
        return []
    chars = state.get("characters", {}) if isinstance(state, dict) else {}
    audit: list[dict[str, Any]] = []
    for raw in changes:
        change = _coerce(raw)
        actor = chars.get(change.owner)
        if actor is None:
            audit.append({
                "owner": change.owner,
                "resource_type": change.resource_type,
                "applied": False,
                "reason": "unknown_actor",
            })
            continue
        if change.resource_type == "spell_slot":
            audit.append(_apply_spell_slot(actor, change))
        elif change.resource_type == "ammunition":
            audit.append(_apply_ammunition(actor, change))
        else:
            audit.append({
                "owner": change.owner,
                "resource_type": change.resource_type,
                "applied": False,
                "reason": "unknown_resource_type",
            })
    return audit
