from dataclasses import asdict
from trapspringer.schemas.actions import Action
from trapspringer.schemas.resolution import PrivateOutcome, PublicOutcome, ResolutionResult
from trapspringer.services.random_service import RandomService
from trapspringer.rules.rule_queries import attack_target_number, weapon_damage_dice


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
    needed_result = attack_target_number(actor, target)
    needed = int(needed_result.answer)
    roll = rng.roll_dice("1d20", f"attack:{action.actor_id}->{target_id}")
    hit = roll.total >= needed
    private = {"target_id": target_id, "needed": needed, "attack_roll": asdict(roll), "hit": hit, "rule_basis": {"attack": needed_result.locator}}
    mutations = []
    if not hit:
        return ResolutionResult(f"RES-{action.action_id}", "resolved", PrivateOutcome(private), PublicOutcome(f"{actor.name} attacks {target.name}, but misses."))
    damage_result = weapon_damage_dice(actor)
    dmg_roll = rng.roll_dice(str(damage_result.answer), f"damage:{action.actor_id}->{target_id}")
    new_hp = max(0, target.current_hp - dmg_roll.total)
    private["damage_roll"] = asdict(dmg_roll)
    private.setdefault("rule_basis", {})["damage"] = damage_result.locator
    private["damage"] = dmg_roll.total
    private["target_hp_after"] = new_hp
    mutations.append({"path": f"characters.{target_id}.current_hp", "value": new_hp})
    if new_hp <= 0:
        mutations.append({"path": f"characters.{target_id}.status", "value": "defeated"})
        narration = f"{actor.name} hits {target.name} for {dmg_roll.total} damage. {target.name} falls."
    else:
        narration = f"{actor.name} hits {target.name} for {dmg_roll.total} damage."
    return ResolutionResult(f"RES-{action.action_id}", "resolved", PrivateOutcome(private), PublicOutcome(narration), mutations)
