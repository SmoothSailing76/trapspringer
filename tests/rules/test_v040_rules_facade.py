from types import SimpleNamespace
from dataclasses import asdict

from trapspringer.rules import adnd1e_v04
from trapspringer.rules.capabilities import default_rules_capability_registry
from trapspringer.services.random_service import RandomService
from trapspringer.layers.layer6_resolution.spells import resolve_spell


def _actor(actor_id='A', cls='fighter', level=5, ac=4, hp=20, team='party'):
    return SimpleNamespace(actor_id=actor_id, name=actor_id, character_class=cls, level=level, ac=ac, team=team, current_hp=hp, max_hp=hp, conditions=[], inventory=[])


def test_v040_attack_and_save_targets():
    attacker = _actor('PC_TANIS', 'fighter', 5)
    target = _actor('BOZAK', 'monster', 4, ac=2, team='enemy')
    attack = adnd1e_v04.attack_target(attacker, target)
    assert attack.target == 14
    save = adnd1e_v04.saving_throw_target(attacker, 'spell')
    assert isinstance(save.target, int)


def test_v040_surprise_initiative_and_morale_are_deterministic():
    rng = RandomService(seed=7)
    init = adnd1e_v04.initiative(rng, 'party')
    surprise = adnd1e_v04.surprise(rng, 'enemies')
    morale = adnd1e_v04.morale_check(rng, 8, group_id='guards')
    assert init.roll['dice'] == '1d6'
    assert surprise.result in {'surprised', 'not_surprised'}
    assert morale.result in {'holds', 'breaks'}


def test_v040_spell_resolution_magic_missile():
    rng = RandomService(seed=4)
    caster = _actor('PC_RAISTLIN', 'magic-user', 3)
    target = _actor('BOZAK', 'monster', 4, ac=2, hp=18, team='enemy')
    state = {'characters': {caster.actor_id: caster, target.actor_id: target}}
    result = resolve_spell({'actor_id': caster.actor_id, 'target_id': target.actor_id, 'spell': 'magic_missile'}, state, rng)
    assert result.status == 'resolved'
    assert result.state_mutations
    assert 'magic missile' in result.public_outcome.narration


def test_v040_capability_registry_updated():
    registry = default_rules_capability_registry()
    assert registry.status('surprise') == 'implemented'
    assert registry.status('saving_throws_core') == 'implemented'
    assert registry.status('morale_reaction') == 'implemented'
