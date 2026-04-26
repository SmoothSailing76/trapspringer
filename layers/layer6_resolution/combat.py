from __future__ import annotations

from dataclasses import asdict

from trapspringer.schemas.actions import Action
from trapspringer.schemas.resolution import PrivateOutcome, PublicOutcome, ResolutionResult, ResourceChange
from trapspringer.services.random_service import RandomService
from trapspringer.rules.rule_queries import attack_target_number, weapon_damage_dice
from trapspringer.rules import adnd1e_v04


def _retarget_if_needed(action: Action, state: dict, target_id: str | None) -> str | None:
    chars = state["characters"]
    target = chars.get(target_id) if target_id else None
    if target is not None and getattr(target, "is_active", False):
        return target_id
    actor = chars[action.actor_id]
    wanted_team = "enemy" if getattr(actor, "team", None) == "party" else "party"
    for aid, c in chars.items():
        if getattr(c, "team", None) == wanted_team and getattr(c, "is_active", False):
            if aid == "NPC_TOEDE" and state["module"].world_flags.get("toede_fled"):
                continue
            return aid
    return None


def resolve_wait(action: Action, state: dict, rng: RandomService) -> ResolutionResult:
    actor = state["characters"][action.actor_id]
    return ResolutionResult(f"RES-{action.action_id}", "resolved", PrivateOutcome({"action": "wait"}), PublicOutcome(f"{actor.name} holds position and watches for an opening."))


def resolve_move(action: Action, state: dict, map_service, rng: RandomService) -> ResolutionResult:
    actor = state["characters"][action.actor_id]
    dest = action.target.id if action.target else action.extra.get("destination")
    mutations = [{"path": f"characters.{action.actor_id}.location.zone", "value": dest}]
    if map_service:
        try:
            map_service.place_entity("DL1_EVENT_1_AMBUSH", action.actor_id, dest)
        except Exception:
            pass
    return ResolutionResult(f"RES-{action.action_id}", "resolved", PrivateOutcome({"moved_to": dest}), PublicOutcome(f"{actor.name} moves to {str(dest).replace('_', ' ')}."), mutations)


def _apply_hit_damage(action: Action, actor, target, target_id: str, rng: RandomService, damage_dice: str | None = None, attack_private: dict | None = None) -> ResolutionResult:
    attack_private = attack_private or {}
    damage_result = weapon_damage_dice(actor)
    dice = damage_dice or str(damage_result.answer)
    dmg_roll = rng.roll_dice(dice, f"damage:{action.actor_id}->{target_id}")
    new_hp = max(0, target.current_hp - dmg_roll.total)
    private = dict(attack_private)
    private["damage_roll"] = asdict(dmg_roll)
    private.setdefault("rule_basis", {})["damage"] = damage_result.locator
    private["damage"] = dmg_roll.total
    private["target_hp_after"] = new_hp
    mutations = [{"path": f"characters.{target_id}.current_hp", "value": new_hp}]
    if new_hp <= 0:
        mutations.append({"path": f"characters.{target_id}.status", "value": "defeated"})
        narration = f"{actor.name} hits {target.name} for {dmg_roll.total} damage. {target.name} falls."
    else:
        narration = f"{actor.name} hits {target.name} for {dmg_roll.total} damage."
    return ResolutionResult(f"RES-{action.action_id}", "resolved", PrivateOutcome(private), PublicOutcome(narration), mutations)


def resolve_melee_attack(action: Action, state: dict, rng: RandomService) -> ResolutionResult:
    chars = state["characters"]
    actor = chars[action.actor_id]
    if not getattr(actor, "is_active", False):
        return ResolutionResult(f"RES-{action.action_id}", "no_effect", PrivateOutcome({"actor_inactive": True}), PublicOutcome(None))
    target_id = action.extra.get("resolved_target_id") or (action.target.id if action.target else None)
    target_id = _retarget_if_needed(action, state, target_id)
    if target_id is None:
        return ResolutionResult(f"RES-{action.action_id}", "no_effect", PrivateOutcome({"no_target": True}), PublicOutcome(f"{actor.name} has no available target."))
    target = chars[target_id]
    needed_result = attack_target_number(actor, target, action.extra.get("modifiers"))
    needed = int(needed_result.answer)
    roll = rng.roll_dice("1d20", f"attack:{action.actor_id}->{target_id}")
    hit = roll.total >= needed
    private = {"target_id": target_id, "needed": needed, "attack_roll": asdict(roll), "hit": hit, "rule_basis": {"attack": needed_result.locator}}
    if not hit:
        return ResolutionResult(f"RES-{action.action_id}", "resolved", PrivateOutcome(private), PublicOutcome(f"{actor.name} attacks {target.name}, but misses."))
    return _apply_hit_damage(action, actor, target, target_id, rng, attack_private=private)


def resolve_missile_attack(action: Action, state: dict, rng: RandomService) -> ResolutionResult:
    chars = state["characters"]
    actor = chars[action.actor_id]
    target_id = action.extra.get("resolved_target_id") or (action.target.id if action.target else None)
    target_id = _retarget_if_needed(action, state, target_id)
    if target_id is None:
        return ResolutionResult(f"RES-{action.action_id}", "no_effect", PrivateOutcome({"no_target": True}), PublicOutcome(f"{actor.name} has no clear missile target."))
    target = chars[target_id]
    range_band = action.extra.get("range_band", "short")
    range_mod = {"short": 0, "medium": -2, "long": -5}.get(str(range_band), 0)
    cover_mod = int(action.extra.get("cover_modifier", 0) or 0)
    needed_result = attack_target_number(actor, target, {"range": range_mod, "cover": cover_mod})
    roll = rng.roll_dice("1d20", f"missile:{action.actor_id}->{target_id}")
    hit = roll.total >= int(needed_result.answer)
    private = {"target_id": target_id, "range_band": range_band, "needed": needed_result.answer, "attack_roll": asdict(roll), "hit": hit, "rule_basis": {"attack": needed_result.locator}}
    resources = [ResourceChange(action.actor_id, "ammunition", -1, "missile attack")]
    if not hit:
        return ResolutionResult(f"RES-{action.action_id}", "resolved", PrivateOutcome(private), PublicOutcome(f"{actor.name} looses a missile at {target.name}, but misses."), resource_changes=resources)
    result = _apply_hit_damage(action, actor, target, target_id, rng, damage_dice=action.extra.get("damage_dice") or "1d6", attack_private=private)
    result.resource_changes.extend(resources)
    result.public_outcome.narration = result.public_outcome.narration.replace("hits", "strikes")
    return result


def resolve_initiative(rng: RandomService) -> dict:
    party = adnd1e_v04.initiative(rng, "party")
    enemies = adnd1e_v04.initiative(rng, "enemies")
    winner = "party" if int(party.result or 0) >= int(enemies.result or 0) else "enemies"
    return {"party": party, "enemies": enemies, "winner": winner}


def resolve_surprise(side: str, rng: RandomService, threshold: int = 2) -> adnd1e_v04.RuleCheck:
    return adnd1e_v04.surprise(rng, side, threshold=threshold)
