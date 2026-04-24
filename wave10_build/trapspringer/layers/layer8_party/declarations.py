from __future__ import annotations

from trapspringer.schemas.actions import Action, ActionContext, ActionTarget
from trapspringer.schemas.declarations import CallerSummary, Declaration, DeclarationSet
from trapspringer.schemas.party import Proposal

DEFAULT_ACTIONS = {
    "PC_TASSLEHOFF": "I dart at the nearest hobgoblin with my hoopak.",
    "PC_STURM": "I engage the nearest hobgoblin and hold the front.",
    "PC_CARAMON": "I move up and swing at the closest hobgoblin.",
    "PC_RAISTLIN": "I stay back and wait for a clear opening.",
    "PC_FLINT": "I plant my feet and attack the nearest hobgoblin.",
    "PC_TANIS": "I strike the nearest hobgoblin.",
}


def build_default_combat_declarations(simulated_actor_ids: list[str]) -> DeclarationSet:
    decls: list[Declaration] = []
    ctx = ActionContext(mode="combat", phase="declaration", scene_id="DL1_EVENT_1_AMBUSH")
    for idx, actor_id in enumerate(simulated_actor_ids, start=1):
        if actor_id == "PC_RAISTLIN":
            action = Action(f"ACT-SIM-{idx:02d}", actor_id, "wait", ctx, spoken_text=DEFAULT_ACTIONS[actor_id])
        else:
            action = Action(
                f"ACT-SIM-{idx:02d}", actor_id, "melee_attack", ctx,
                target=ActionTarget("actor", "nearest_enemy"),
                spoken_text=DEFAULT_ACTIONS.get(actor_id, "I attack the nearest enemy."),
            )
        decls.append(Declaration(f"DEC-SIM-{idx:02d}", actor_id, action.spoken_text or "", action))
    return DeclarationSet(declarations=decls, caller_summary=CallerSummary("PC_TANIS", "The party holds formation and attacks the nearest hobgoblins while Raistlin hangs back."))


def build_scene_declarations_from_proposals(scene_id: str, simulated_actor_ids: list[str], proposals: list[Proposal]) -> DeclarationSet:
    """Wave 9 non-combat declarations used by demos/tests.

    These declarations are still intentionally simple so Layer 5 can validate or reject
    them later; the improvement is that they come from personality proposals rather than
    a single hive-mind default.
    """
    decls: list[Declaration] = []
    ctx = ActionContext(mode="exploration", phase="declaration", scene_id=scene_id)
    by_actor: dict[str, Proposal] = {}
    for proposal in proposals:
        for actor_id in simulated_actor_ids:
            token = actor_id.replace("PC_", "").replace("NPC_", "").upper()
            if token in proposal.player_id.upper() and actor_id not in by_actor:
                by_actor[actor_id] = proposal

    for idx, actor_id in enumerate(simulated_actor_ids, start=1):
        proposal = by_actor.get(actor_id)
        action_type = "wait"
        target = None
        text = "I follow the caller's plan."
        if proposal:
            hint = proposal.action_hint or {}
            action_type = str(hint.get("action_type", "wait"))
            target_id = hint.get("target")
            if target_id:
                target = ActionTarget("scene_feature", str(target_id))
            text = proposal.spoken_text
        action = Action(f"ACT-SCENE-SIM-{idx:02d}", actor_id, action_type, ctx, target=target, spoken_text=text)
        decls.append(Declaration(f"DEC-SCENE-SIM-{idx:02d}", actor_id, text, action))
    return DeclarationSet(declarations=decls, caller_summary=CallerSummary("PC_TANIS", "The party follows the converged scene plan."))
