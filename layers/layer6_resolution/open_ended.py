from __future__ import annotations

from typing import Any

from trapspringer.layers.layer4_procedure.open_ended import OpenEndedIntent
from trapspringer.schemas.resolution import PrivateOutcome, PublicOutcome, ResolutionResult, FollowupCheck


def _scene(state: dict[str, Any]) -> str:
    try:
        return str(state["campaign"].active_scene_id or state["scene"].scene_id)
    except Exception:
        return "unknown"


def resolve_open_ended_intent(intent: OpenEndedIntent, state: dict[str, Any]) -> ResolutionResult:
    """Resolve supported non-mainline choices into auditable state effects.

    v0.5 intentionally supports branch *tracking* and safe consequences rather
    than trying to fully DM every creative plan. Unsupported inputs are routed to
    explicit human-ruling state instead of being silently ignored.
    """
    scene_id = _scene(state)
    base = f"RES-V050-{intent.intent_type.upper()}"

    if intent.intent_type == "refuse_hook":
        return ResolutionResult(
            base,
            "resolved_branch",
            PrivateOutcome({"branch": "refuse_hook", "scene_id": scene_id}),
            PublicOutcome("The party can refuse the obvious road to Xak Tsaroth. The world does not pause: refugees keep moving, rumors worsen, and the Dragonarmy clock advances."),
            [
                {"path": "module.world_flags.branch_refused_main_hook", "value": True},
                {"path": "module.world_flags.current_route", "value": "alternate_or_avoidance"},
                {"path": "time.day", "value": int(getattr(state.get("time"), "day", 1)) + 1},
            ],
            followup_checks=[FollowupCheck("event_clock", "dragonarmy_march", "after_delay")],
        )

    if intent.intent_type == "retreat":
        return ResolutionResult(
            base,
            "resolved_branch",
            PrivateOutcome({"branch": "retreat", "from_scene": scene_id}),
            PublicOutcome("The party withdraws from the immediate danger. The route behind remains usable, but time passes and any alerted enemies may react."),
            [
                {"path": "module.world_flags.party_retreating", "value": True},
                {"path": "module.world_flags.last_retreat_from", "value": scene_id},
                {"path": "time.turn", "value": int(getattr(state.get("time"), "turn", 0)) + 1},
            ],
            followup_checks=[FollowupCheck("wandering_encounter", "current_area", "after_retreat")],
        )

    if intent.intent_type == "split_party":
        return ResolutionResult(
            base,
            "resolved_branch",
            PrivateOutcome({"branch": "split_party", "scene_id": scene_id, "risk": "high"}),
            PublicOutcome("The table commits to a split-party plan. The DM will track separate groups and only share information across groups when characters can actually communicate."),
            [
                {"path": "module.world_flags.party_split_active", "value": True},
                {"path": "module.world_flags.party_split_origin", "value": scene_id},
            ],
            followup_checks=[FollowupCheck("knowledge_boundary", "split_party", "immediate")],
        )

    if intent.intent_type == "take_prisoner":
        return ResolutionResult(
            base,
            "resolved_branch",
            PrivateOutcome({"branch": "take_prisoner", "candidate": intent.target or "enemy"}),
            PublicOutcome("The party tries to take an enemy alive. If combat positioning allows it, the captive can be bound and questioned after the fight."),
            [
                {"path": "module.world_flags.prisoner_taken", "value": True},
                {"path": "module.world_flags.prisoner_source_scene", "value": scene_id},
            ],
            followup_checks=[FollowupCheck("social_interrogation", "prisoner", "after_combat")],
        )

    if intent.intent_type == "interrogate_prisoner":
        return ResolutionResult(
            base,
            "resolved_branch",
            PrivateOutcome({"branch": "interrogate_prisoner", "known_limit": "prisoner_knows_orders_only"}),
            PublicOutcome("The captive can answer only what they plausibly know: orders, routes recently traveled, who commanded them, and what they were told to seek."),
            [
                {"path": "module.world_flags.prisoner_interrogated", "value": True},
                {"path": "module.world_flags.prisoner_info_unlocked", "value": "orders_and_route"},
            ],
            knowledge_effects=[{"fact_id": "F-PRISONER-ORDERS", "proposition": "Captured enemies know limited orders and recent routes, not the full module truth.", "visibility_after": "party_known", "discovered_by": "PARTY"}],
        )

    if intent.intent_type == "key_item_risk":
        return ResolutionResult(
            base,
            "resolved_branch",
            PrivateOutcome({"branch": "key_item_risk", "item": "blue_crystal_staff", "requires_dm_confirmation": True}),
            PublicOutcome("That choice risks a critical quest item. The simulator marks the moment for explicit confirmation or a human DM ruling before the campaign is allowed to become unwinnable."),
            [
                {"path": "module.world_flags.key_item_risk_pending", "value": True},
                {"path": "module.world_flags.key_item_risk_item", "value": "blue_crystal_staff"},
            ],
            followup_checks=[FollowupCheck("requires_human_ruling", "blue_crystal_staff", "before_mutating_item")],
        )

    if intent.intent_type == "search_alternate_route":
        return ResolutionResult(
            base,
            "resolved_branch",
            PrivateOutcome({"branch": "search_alternate_route", "scene_id": scene_id}),
            PublicOutcome("The party slows down and searches for another way. Obvious exits are mapped; hidden routes still require the correct area, time, and discovery trigger."),
            [
                {"path": "module.world_flags.alternate_route_search_active", "value": True},
                {"path": "time.turn", "value": int(getattr(state.get("time"), "turn", 0)) + 1},
            ],
            followup_checks=[FollowupCheck("search_check", "current_area", "after_turn")],
        )

    if intent.intent_type == "rest_or_delay":
        return ResolutionResult(
            base,
            "resolved_branch",
            PrivateOutcome({"branch": "rest_or_delay", "scene_id": scene_id}),
            PublicOutcome("The party stops to rest or wait. Watches can be set, but time passes and encounter/event clocks advance."),
            [
                {"path": "module.world_flags.party_resting_or_delaying", "value": True},
                {"path": "time.hour", "value": int(getattr(state.get("time"), "hour", 20)) + 8},
            ],
            followup_checks=[FollowupCheck("rest_encounter_check", "current_area", "during_rest")],
        )

    return ResolutionResult(
        base,
        "requires_human_ruling",
        PrivateOutcome({"raw_text": intent.raw_text, "intent_type": intent.intent_type}),
        PublicOutcome("That action is outside the supported v0.5 model. A human ruling is required before it can change the game state."),
        [{"path": "module.world_flags.human_ruling_required", "value": True}],
    )
