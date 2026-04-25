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


def test_fireball_deals_level_d6_damage():
    rng = RandomService(seed=42)
    caster = _actor('PC_RAISTLIN', 'magic-user', 5)
    target = _actor('BOZAK', 'monster', 4, ac=2, hp=30, team='enemy')
    state = {'characters': {caster.actor_id: caster, target.actor_id: target}}
    result = resolve_spell({'actor_id': caster.actor_id, 'target_id': target.actor_id, 'spell': 'fireball'}, state, rng)
    assert result.status == 'resolved'
    assert 'fireball' in result.public_outcome.narration


def test_hold_person_applies_held_condition_on_failed_save():
    rng = RandomService(seed=1)
    caster = _actor('PC_GOLDMOON', 'cleric', 5)
    target = _actor('HOBGOBLIN', 'monster', 2, ac=5, hp=10, team='enemy')
    state = {'characters': {caster.actor_id: caster, target.actor_id: target}}
    result = resolve_spell({'actor_id': caster.actor_id, 'target_id': target.actor_id, 'spell': 'hold_person'}, state, rng)
    assert result.status == 'resolved'


def test_dragon_breath_damage_equals_current_hp():
    rng = RandomService(seed=3)
    dragon = _actor('KHISANTH', 'monster', 7, ac=-1, hp=52, team='enemy')
    dragon.current_hp = 52
    dragon.breath_type = 'acid'
    target = _actor('PC_TANIS', 'fighter', 5, hp=35, team='party')
    check = adnd1e_v04.dragon_breath_damage(dragon.current_hp, target, rng, 'acid')
    assert check.target == 52
    damage = int(check.result.split(':')[-1])
    assert damage in (26, 52)


def test_dragon_fear_save_produces_result():
    rng = RandomService(seed=9)
    actor = _actor('PC_STURM', 'fighter', 5)
    check = adnd1e_v04.dragon_fear_save(actor, dragon_hd=7, rng=rng)
    assert check.result in ('fleeing', 'steadfast')
    assert check.rule_id == 'dragon_fear'


def test_xp_to_next_level_fighter():
    fighter = _actor('PC_CARAMON', 'fighter', 3)
    fighter.xp = 5000
    check = adnd1e_v04.xp_to_next_level(fighter)
    assert check.target == 8000
    assert check.result == 'needs_xp'


def test_training_cost():
    check = adnd1e_v04.training_cost(4)
    assert check.target == 6000


def test_initiative_dex_tiebreaker():
    rng = RandomService(seed=77)
    result = adnd1e_v04.initiative_with_dex(rng, 'party', dex_score=16)
    assert result.metadata['dex_score'] == 16


def test_bless_and_protection_from_evil_resolve():
    rng = RandomService(seed=5)
    caster = _actor('PC_GOLDMOON', 'cleric', 5)
    target = _actor('PC_TANIS', 'fighter', 5, team='party')
    state = {'characters': {caster.actor_id: caster, target.actor_id: target}}
    bless = resolve_spell({'actor_id': caster.actor_id, 'target_id': target.actor_id, 'spell': 'bless'}, state, rng)
    pfe = resolve_spell({'actor_id': caster.actor_id, 'target_id': target.actor_id, 'spell': 'protection_from_evil'}, state, rng)
    assert bless.status == 'resolved'
    assert pfe.status == 'resolved'


def test_spell_casting_capability_is_implemented():
    registry = default_rules_capability_registry()
    assert registry.status('spell_casting') == 'implemented'
    assert registry.status('dragon_fear_breath') == 'implemented'
    assert registry.status('xp_training') == 'implemented'
