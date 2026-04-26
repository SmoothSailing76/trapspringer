"""Tests for ResourceChange application — spell slot decrement and ammunition no-op.

Before this code path was wired, spell and missile resolvers emitted
ResourceChange records that nothing read. So magic-users could cast the
same spell unlimited times. These tests pin the new behavior:
  - spell_slot removes the spell from actor.spells (Vancian)
  - already-expended spells silently no-op
  - ammunition is recorded as intent-only until inventory has counts
"""
from __future__ import annotations

from trapspringer.engine.orchestrator import Orchestrator
from trapspringer.layers.layer3_state.resources import apply_resource_changes
from trapspringer.layers.layer6_resolution.spells import resolve_spell
from trapspringer.schemas.resolution import ResourceChange
from trapspringer.services.random_service import RandomService


def test_spell_slot_decrement_removes_spell_from_actor():
    orch = Orchestrator()
    orch.start_campaign(campaign_id="RES-TEST-SPELL")
    state = orch.layer3.read_state()
    raistlin = state["characters"]["PC_RAISTLIN"]
    assert "magic_missile" in raistlin.spells

    audit = apply_resource_changes(state, [ResourceChange("PC_RAISTLIN", "spell_slot", -1, "magic_missile")])

    assert audit == [{
        "owner": "PC_RAISTLIN",
        "resource_type": "spell_slot",
        "applied": True,
        "spell": "magic_missile",
        "remaining_spells": ["sleep", "web"],
    }]
    assert raistlin.spells == ["sleep", "web"]


def test_spell_slot_decrement_when_already_expended_is_a_safe_noop():
    orch = Orchestrator()
    orch.start_campaign(campaign_id="RES-TEST-EXPENDED")
    state = orch.layer3.read_state()
    raistlin = state["characters"]["PC_RAISTLIN"]
    raistlin.spells = ["sleep"]  # magic_missile already expended

    audit = apply_resource_changes(state, [ResourceChange("PC_RAISTLIN", "spell_slot", -1, "magic_missile")])

    assert audit[0]["applied"] is False
    assert audit[0]["reason"] == "spell_already_expended"
    assert raistlin.spells == ["sleep"]  # unchanged


def test_ammunition_records_intent_but_does_not_mutate():
    orch = Orchestrator()
    orch.start_campaign(campaign_id="RES-TEST-AMMO")
    state = orch.layer3.read_state()
    tanis = state["characters"]["PC_TANIS"]
    inventory_before = list(tanis.inventory)

    audit = apply_resource_changes(state, [ResourceChange("PC_TANIS", "ammunition", -1, "missile attack")])

    assert audit[0]["applied"] is False
    assert audit[0]["reason"] == "no_inventory_count_schema"
    assert tanis.inventory == inventory_before


def test_unknown_actor_audited_not_raised():
    orch = Orchestrator()
    orch.start_campaign(campaign_id="RES-TEST-UNKNOWN")
    state = orch.layer3.read_state()

    audit = apply_resource_changes(state, [ResourceChange("PC_GHOST", "spell_slot", -1, "fireball")])

    assert audit[0]["applied"] is False
    assert audit[0]["reason"] == "unknown_actor"


def test_full_spell_resolution_decrements_slot_via_orchestrator():
    """Integration: resolve_spell emits a ResourceChange; the orchestrator's
    commit path now applies it through StateService.commit_resource_changes."""
    orch = Orchestrator()
    orch.start_campaign(campaign_id="RES-TEST-INT")
    state = orch.layer3.read_state()
    raistlin = state["characters"]["PC_RAISTLIN"]
    target_id = next(aid for aid in state["characters"] if aid.startswith("HOBGOBLIN_EVENT1_"))
    assert "magic_missile" in raistlin.spells

    rng = RandomService(seed=4)
    result = resolve_spell(
        {"actor_id": "PC_RAISTLIN", "target_id": target_id, "spell": "magic_missile"},
        state, rng,
    )
    assert result.resource_changes, "expected the spell resolver to emit a spell_slot change"

    orch._commit_resolution_result(result)

    assert "magic_missile" not in raistlin.spells
