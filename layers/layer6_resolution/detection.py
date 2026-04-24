from __future__ import annotations
from trapspringer.services.random_service import RandomService


def resolve_detection(request, rng: RandomService | None = None):
    rng = rng or RandomService(seed=1)
    chance = int(request.get('chance_percent', 30))
    roll = rng.roll_dice('1d100', f"detect:{request.get('target', 'hidden_feature')}")
    found = roll.total <= chance
    return {'status': 'resolved', 'found': found, 'roll': roll.__dict__, 'chance_percent': chance, 'target': request.get('target')}
