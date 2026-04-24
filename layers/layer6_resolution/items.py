from __future__ import annotations
from dataclasses import asdict
from typing import Any
from trapspringer.rules import adnd1e_v04
from trapspringer.services.random_service import RandomService


def resolve_item_use(request):
    item = request.get('item', 'item')
    if item == 'blue_crystal_staff' and request.get('mode') == 'heal':
        return {'status': 'resolved', 'item': item, 'effect': 'heal', 'charges_delta': -1}
    return {'status': 'resolved', 'item': item}


def resolve_item_save(request: dict[str, Any], rng: RandomService | None = None):
    rng = rng or RandomService(seed=1)
    return asdict(adnd1e_v04.item_save(str(request.get('material', 'wood')), str(request.get('attack_form', 'fire')), rng, int(request.get('magical_bonus', 0))))
