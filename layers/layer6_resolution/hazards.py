from __future__ import annotations
from typing import Any
from trapspringer.rules import adnd1e_v04
from trapspringer.schemas.resolution import PrivateOutcome, PublicOutcome, ResolutionResult
from trapspringer.services.random_service import RandomService


def resolve_hazard(request: dict[str, Any], state: dict | None = None, rng: RandomService | None = None):
    rng = rng or RandomService(seed=1)
    hazard = request.get('hazard', 'falling_debris')
    actor = request.get('actor')
    if hazard == 'falling_debris':
        chance = int(request.get('chance_percent', 15))
        roll = rng.roll_dice('1d100', 'hazard:falling_debris')
        hit = roll.total <= chance
        dmg = rng.roll_dice(str(request.get('damage', '1d12')), 'hazard_damage:falling_debris') if hit else None
        return {'hazard': hazard, 'actor': actor, 'hit': hit, 'roll': roll.__dict__, 'damage_roll': dmg.__dict__ if dmg else None}
    if hazard == 'saving_throw':
        check = adnd1e_v04.roll_saving_throw(actor, request.get('category', 'breath'), rng) if actor is not None else None
        return check.__dict__ if check else {'hazard': hazard, 'status': 'no_actor'}
    return {'status': 'resolved', 'hazard': hazard}


def resolve_falling_damage(actor_id: str, feet: int, rng: RandomService | None = None) -> ResolutionResult:
    rng = rng or RandomService(seed=1)
    dice = max(1, min(20, feet // 10))
    roll = rng.roll_dice(f'{dice}d6', f'falling_damage:{actor_id}')
    return ResolutionResult('RES-FALL', 'resolved', PrivateOutcome({'feet': feet, 'damage_roll': roll.__dict__}), PublicOutcome(f'{actor_id} falls {feet} feet and takes {roll.total} damage.'), [{'path': f'characters.{actor_id}.current_hp_delta', 'value': -roll.total}])
