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
    if spell["type"] == "area_damage":
        caster_level = int(getattr(chars.get(actor_id), "level", 1) or 1)
        dice_expr = f"{caster_level}d6"
        roll = rng.roll_dice(dice_expr, f"spell_damage:{spell_name}:{actor_id}")
        private["damage_roll"] = asdict(roll)
        private["area"] = spell.get("area", "area")
        if target is not None:
            save = adnd1e_v04.roll_saving_throw(target, "spell", rng)
            private["saving_throw"] = asdict(save)
            damage = roll.total // 2 if save.success else roll.total
            new_hp = max(0, target.current_hp - damage)
            private["damage_taken"] = damage
            private["target_hp_after"] = new_hp
            mutations.append({"path": f"characters.{target_id}.current_hp", "value": new_hp})
            if new_hp <= 0:
                mutations.append({"path": f"characters.{target_id}.status", "value": "defeated"})
            saved_text = " (save: half damage)" if save.success else ""
            return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} casts {spell_name.replace('_', ' ')} for {damage} damage{saved_text}."), mutations, resource_changes=resources)
        return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} casts {spell_name.replace('_', ' ')} ({roll.total} damage potential)."), resource_changes=resources)
    if spell["type"] == "hold":
        if target is not None:
            save = adnd1e_v04.roll_saving_throw(target, "spell", rng)
            private["saving_throw"] = asdict(save)
            if not save.success:
                dur_roll = rng.roll_dice("1d4", f"hold_duration:{actor_id}")
                private["duration_rounds"] = dur_roll.total + 3
                mutations.append({"path": f"characters.{target_id}.conditions", "value": list(set(target.conditions + ["held"]))})
                return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} casts hold person; {getattr(target, 'name', target_id)} is held rigid for {private['duration_rounds']} rounds."), mutations, resource_changes=resources)
            return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} casts hold person; {getattr(target, 'name', target_id)} resists."), resource_changes=resources)
        return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} casts hold person."), resource_changes=resources)
    if spell["type"] == "buff":
        bonus_attack = int(spell.get("bonus_attack", 0))
        bonus_save = int(spell.get("bonus_save", 0))
        bonus_ac = int(spell.get("bonus_ac", 0))
        if target is not None:
            conditions = list(set(target.conditions + [f"blessed:{bonus_attack}:{bonus_save}"] if bonus_attack else target.conditions + [f"protected:{bonus_ac}:{bonus_save}"]))
            mutations.append({"path": f"characters.{target_id}.conditions", "value": conditions})
        private["buff"] = {"bonus_attack": bonus_attack, "bonus_save": bonus_save, "bonus_ac": bonus_ac}
        return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} casts {spell_name.replace('_', ' ')}."), mutations, resource_changes=resources)
    if spell["type"] == "touch_damage":
        if target is not None:
            roll = rng.roll_dice(str(spell.get("damage", "1d8")), f"spell_damage:{spell_name}:{actor_id}->{target_id}")
            new_hp = max(0, target.current_hp - roll.total)
            private["damage_roll"] = asdict(roll)
            private["target_hp_after"] = new_hp
            mutations.append({"path": f"characters.{target_id}.current_hp", "value": new_hp})
            if new_hp <= 0:
                mutations.append({"path": f"characters.{target_id}.status", "value": "defeated"})
            return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} touches {getattr(target, 'name', target_id)} for {roll.total} damage."), mutations, resource_changes=resources)
    if spell["type"] == "dispel":
        if target is not None:
            conditions = [c for c in target.conditions if not any(c.startswith(p) for p in ("blessed:", "protected:", "held", "webbed"))]
            mutations.append({"path": f"characters.{target_id}.conditions", "value": conditions})
            return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} dispels magic on {getattr(target, 'name', target_id)}."), mutations, resource_changes=resources)
        return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} casts dispel magic on the area."), resource_changes=resources)
    return ResolutionResult("RES-SPELL", "resolved", PrivateOutcome(private), PublicOutcome(f"{getattr(actor, 'name', actor_id)} casts {spell_name.replace('_', ' ')}."), resource_changes=resources)


def spell_interrupted(caster_id: str, damage_taken_before_completion: int, spell_name: str) -> dict[str, Any]:
    interrupted = damage_taken_before_completion > 0
    return {"caster_id": caster_id, "spell_name": spell_name, "interrupted": interrupted, "status": "partial", "notes": "v0.4 interruption helper: damage before completion disrupts the spell."}
