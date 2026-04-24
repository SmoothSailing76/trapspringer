from __future__ import annotations
from dataclasses import asdict
from typing import Any
from trapspringer.rules import adnd1e_v04
from trapspringer.services.random_service import RandomService


def resolve_morale(request: dict[str, Any], rng: RandomService | None = None):
    rng = rng or RandomService(seed=1)
    return asdict(adnd1e_v04.morale_check(rng, int(request.get('morale_score', 8)), int(request.get('modifier', 0)), str(request.get('group_id', 'group'))))


def resolve_reaction(request: dict[str, Any], rng: RandomService | None = None):
    rng = rng or RandomService(seed=1)
    return asdict(adnd1e_v04.reaction_check(rng, int(request.get('modifier', 0)), str(request.get('npc_id', 'npc'))))
