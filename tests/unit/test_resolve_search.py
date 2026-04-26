"""End-to-end tests for the search resolver against a real DL1 hidden fact.

Targets F-AREA4-DRACONIAN-AMBUSH, seeded by KnowledgeService and gated on
discovery_conditions=["climb_tree", "spot_hidden_draconians"]. Before these
tests it was unreachable — no action could trigger discovery.
"""
from __future__ import annotations

from trapspringer.engine.orchestrator import Orchestrator
from trapspringer.schemas.actions import Action, ActionContext
from trapspringer.schemas.resolution import ResolutionRequest
from trapspringer.services.random_service import RandomService


def _build_search_request(orchestrator: Orchestrator, target_kind: str, *, actor_id: str = "PC_TANIS") -> ResolutionRequest:
    state = orchestrator.layer3.read_state()
    action = Action(
        action_id="ACT-SEARCH-TEST",
        actor_id=actor_id,
        action_type="search",
        context=ActionContext(mode="exploration", scene_id=state["campaign"].active_scene_id),
        extra={"target_kind": target_kind},
    )
    return ResolutionRequest(
        resolution_id="RES-SEARCH-TEST",
        action_id=action.action_id,
        actor_id=actor_id,
        scene_id=state["campaign"].active_scene_id or "",
        mode="exploration",
        payload={
            "action": action,
            "state": state,
            "knowledge_service": orchestrator.layer2,
        },
    )


def test_successful_search_discovers_seeded_dl1_fact_and_marks_party_known():
    orch = Orchestrator()
    orch.start_campaign(campaign_id="SEARCH-TEST-OK")
    # Force d6=1 (success at default 1-in-6 threshold).
    orch.layer6.rng = RandomService(
        replay_records=[{"roll_id": "ROLL-FORCED", "dice": "1d6", "purpose": "search-test", "raw": [1], "total": 1}]
    )

    fact = orch.layer2.facts.get("F-AREA4-DRACONIAN-AMBUSH")
    assert fact is not None
    assert "PARTY" not in fact.known_by
    assert fact.visibility_class == "dm_private"

    req = _build_search_request(orch, "spot_hidden_draconians")
    result = orch.layer6.resolve(req)

    assert result.status == "resolved"
    assert result.knowledge_effects, "expected a knowledge_effect on a successful search"
    effect = result.knowledge_effects[0]
    assert effect["fact_id"] == "F-AREA4-DRACONIAN-AMBUSH"

    # Apply the effect through Layer 2 (the orchestrator does this in _commit_resolution_result).
    orch.layer2.apply_discovery(effect)
    fact_after = orch.layer2.facts.get("F-AREA4-DRACONIAN-AMBUSH")
    assert "PARTY" in fact_after.known_by
    assert fact_after.visibility_class == "party_known"


def test_failed_search_leaves_fact_hidden():
    orch = Orchestrator()
    orch.start_campaign(campaign_id="SEARCH-TEST-FAIL")
    # Stuff a roll record that always returns d6=6 (worst case) so the search fails.
    orch.layer6.rng = RandomService(
        replay_records=[{"roll_id": "ROLL-FORCED", "dice": "1d6", "purpose": "search-test", "raw": [6], "total": 6}]
    )

    req = _build_search_request(orch, "spot_hidden_draconians")
    result = orch.layer6.resolve(req)

    assert result.status == "resolved"
    assert not result.knowledge_effects
    fact = orch.layer2.facts.get("F-AREA4-DRACONIAN-AMBUSH")
    assert "PARTY" not in fact.known_by
    assert fact.visibility_class == "dm_private"


def test_search_with_unknown_target_kind_finds_nothing():
    orch = Orchestrator()
    orch.start_campaign(campaign_id="SEARCH-TEST-NONE")
    # Empty candidate set — short-circuits before the dice roll.
    req = _build_search_request(orch, "nonexistent_kind")
    result = orch.layer6.resolve(req)

    assert result.status == "resolved"
    assert not result.knowledge_effects
    assert "finds nothing" in (result.public_outcome.narration or "").lower()


def test_search_without_knowledge_service_is_a_safe_noop():
    orch = Orchestrator()
    orch.start_campaign(campaign_id="SEARCH-TEST-NOKS")
    state = orch.layer3.read_state()
    action = Action(
        action_id="ACT-SEARCH-NOKS",
        actor_id="PC_TANIS",
        action_type="search",
        context=ActionContext(mode="exploration"),
        extra={"target_kind": "spot_hidden_draconians"},
    )
    # Deliberately omit knowledge_service from the payload.
    req = ResolutionRequest(
        resolution_id="RES-SEARCH-NOKS",
        action_id=action.action_id,
        actor_id="PC_TANIS",
        scene_id=state["campaign"].active_scene_id or "",
        mode="exploration",
        payload={"action": action, "state": state},
    )
    result = orch.layer6.resolve(req)

    assert result.status == "no_effect"
    assert not result.knowledge_effects
