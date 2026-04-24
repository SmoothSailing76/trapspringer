from __future__ import annotations

from dataclasses import asdict
from typing import Any

from trapspringer.rules import adnd1e_v04
from trapspringer.schemas.resolution import PrivateOutcome, PublicOutcome, ResolutionResult, ResourceChange
from trapspringer.services.random_service import RandomService


def _spell_key(name: str) -> str:
    return name.lower().strip().replace(" ", "_")


def resolve_spell(request: dict[str, Any], state: dict | None = None, rng: RandomService | None = None) -> ResolutionResult:
    rng = rng or RandomService(seed=1)
    state = state or request.get("state", {})
    chars = state.get("characters", {}) if isinstance(state, dict) else {}
    actor_id = request.get("actor_id") or request.get("caster_id") or "UNKNOWN"
    target_id = request.get("target_id")
    spell_name = _spell_key(str(request.get("spell") or request.get("spell_name") or ""))
    spell = adnd1e_v04.SPELLS.get(spell_name)
    if not spell:
        return ResolutionResult("RES-SPELL", "no_effect", PrivateOutcome({"unknown_spell": spell_name}), PublicOutcome(f"The spell {spell_name} is not supported by the v0.4 rules facade."))
    actor = chars.get(actor_id)
    target = chars.get(target_id) if target_id else None
    private = {"spell": spell_name, "actor_id": actor_id, "target_id": target_id, "spell_definition": spell}
    mutations: list[dict[str, Any]] = []
    resources = [ResourceChange(actor_id, "spell_slot", -1, spell_name)]
    if spell["type"] == "damage" and target is not None:
        roll = rng.roll_dice(str(spell.get("damage", "1d4")), f"spell_damage:{spell_name}:{actor_id}->{target_id}", modifiers={"bonus": int(spell.get("bonus", 0) or 0)})
        new_hp = max(0, target.current_hp - roll.total)
        private["damage_roll"] = asdict(roll)
        private["target_hp_after"] = new_hp
        mutations.append({"path": f"characters.{target_id}.current_hp", "value": new_hp})
        if new_hp <= 0:
            mutations.append({"path": f"characters.{target_id}.status", "value": "defeated"})
        return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} casts magic missile at {getattr(target, 'name', target_id)} for {roll.total} damage."), mutations, resource_changes=resources)
    if spell["type"] == "healing" and target is not None:
        roll = rng.roll_dice(str(spell.get("healing", "1d8")), f"spell_heal:{spell_name}:{actor_id}->{target_id}")
        new_hp = min(target.max_hp, target.current_hp + roll.total)
        private["healing_roll"] = asdict(roll)
        private["target_hp_after"] = new_hp
        mutations.append({"path": f"characters.{target_id}.current_hp", "value": new_hp})
        return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} casts cure light wounds; {getattr(target, 'name', target_id)} regains {roll.total} hit points."), mutations, resource_changes=resources)
    if spell["type"] == "control":
        roll = rng.roll_dice(str(spell.get("hit_dice_affected", "2d4")), f"spell_control:{spell_name}:{actor_id}")
        private["hit_dice_affected_roll"] = asdict(roll)
        return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} casts sleep; creatures totaling up to {roll.total} hit dice may be affected."), resource_changes=resources)
    if spell["type"] == "restrain":
        if target is not None:
            save = adnd1e_v04.roll_saving_throw(target, str(spell.get("save", "spell")), rng)
            private["saving_throw"] = asdict(save)
            if not save.success:
                mutations.append({"path": f"characters.{target_id}.conditions", "value": list(set(target.conditions + ["webbed"]))})
            result = "is caught in the web" if not save.success else "breaks clear of the web"
            return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} casts web; {getattr(target, 'name', target_id)} {result}."), mutations, resource_changes=resources)
        return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} casts web, filling the area with sticky strands."), resource_changes=resources)
    return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} casts {spell_name.replace('_', ' ')}."), resource_changes=resources)


def spell_interrupted(caster_id: str, damage_taken_before_completion: int, spell_name: str) -> dict[str, Any]:
    interrupted = damage_taken_before_completion > 0
    return {"caster_id": caster_id, "spell_name": spell_name, "interrupted": interrupted, "status": "partial", "notes": "v0.4 interruption helper: damage before completion disrupts the spell."}
